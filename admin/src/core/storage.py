from minio import Minio
from minio.error import S3Error
from minio.commonconfig import ENABLED, Filter
from minio.lifecycleconfig import LifecycleConfig, Rule, Expiration
import io
import mimetypes
import uuid
from datetime import timedelta
from pathlib import Path
from typing import BinaryIO, Optional, Tuple
from werkzeug.datastructures import FileStorage
import logging


class StorageError(Exception):
    """Excepción base para errores de Storage"""
    pass


class StorageConnectionError(StorageError):
    """Error de conexión con MinIO"""
    pass


class StorageUploadError(StorageError):
    """Error al subir archivos"""
    pass


class StorageDeleteError(StorageError):
    """Error al eliminar archivos"""
    pass


class Storage:
    """
    Wrapper para MinIO con funcionalidades mejoradas:
    - Manejo robusto de errores
    - Soporte para múltiples tipos de almacenamiento
    - URLs pre-firmadas y públicas
    - Validación de archivos
    - Gestión de políticas de bucket
    """

    # Límites por defecto
    DEFAULT_MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
    DEFAULT_URL_EXPIRY = timedelta(days=7)

    # Tipos MIME permitidos por defecto
    ALLOWED_MIME_TYPES = {
        'image/jpeg', 'image/png', 'image/webp',
    }

    def __init__(self, app=None):
        self._client = None
        self._bucket_name = None
        self._endpoint = None
        self._secure = False
        self._logger = logging.getLogger(__name__)

        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """Inicializa el cliente de MinIO con la aplicación Flask"""
        endpoint = app.config.get("MINIO_SERVER", "localhost:9000")
        access_key = app.config.get("MINIO_ACCESS_KEY", "minioadmin")
        secret_key = app.config.get("MINIO_SECRET_KEY", "minioadmin")
        self._secure = app.config.get("MINIO_SECURE", False)
        self._bucket_name = app.config.get("MINIO_BUCKET", "proyecto")

        # Configuraciones adicionales
        self.max_file_size = app.config.get("MAX_FILE_SIZE", self.DEFAULT_MAX_FILE_SIZE)
        self.url_expiry = timedelta(days=app.config.get("MINIO_URL_EXPIRY_DAYS", 7))

        # Limpiar el endpoint
        self._endpoint = endpoint.replace("http://", "").replace("https://", "")
        self._logger = app.logger

        try:
            # Crear cliente MinIO
            self._client = Minio(
                self._endpoint,
                access_key=access_key,
                secret_key=secret_key,
                secure=self._secure,
            )

            # Verificar conexión
            self._client.list_buckets()
            self._logger.info(f"✓ Conexión con MinIO establecida: {self._endpoint}")

            # Inicializar bucket
            self._ensure_bucket_exists(self._bucket_name)

        except S3Error as e:
            self._logger.error(f"✗ Error S3 al conectar con MinIO: {e}")
            raise StorageConnectionError(f"No se pudo conectar con MinIO: {e}")
        except Exception as e:
            self._logger.error(f"✗ Error inesperado al inicializar MinIO: {e}")
            raise StorageConnectionError(f"Error de inicialización: {e}")

        # Adjuntar al contexto Flask
        app.storage = self
        return app

    def _ensure_bucket_exists(self, bucket_name: str) -> None:
        """Asegura que el bucket exista, lo crea si no existe"""
        try:
            if not self._client.bucket_exists(bucket_name):
                self._client.make_bucket(bucket_name)
                self._logger.info(f"✓ Bucket creado: {bucket_name}")
            else:
                self._logger.info(f"✓ Bucket existente: {bucket_name}")
        except S3Error as e:
            raise StorageError(f"Error al verificar/crear bucket {bucket_name}: {e}")

    def _validate_file(self, file_storage: FileStorage, max_size: Optional[int] = None) -> Tuple[str, int]:
        """
        Valida el archivo antes de subirlo

        Returns:
            Tuple[str, int]: (content_type, file_size)
        """
        max_size = max_size or self.max_file_size

        # Obtener tipo MIME
        content_type = mimetypes.guess_type(file_storage.filename)[0]
        if not content_type:
            content_type = file_storage.content_type or "application/octet-stream"

        # Validar tipo MIME si está habilitada la validación
        if hasattr(self, 'validate_mime_types') and self.validate_mime_types:
            if content_type not in self.ALLOWED_MIME_TYPES:
                raise StorageUploadError(
                    f"Tipo de archivo no permitido: {content_type}. "
                    f"Permitidos: {', '.join(self.ALLOWED_MIME_TYPES)}"
                )

        # Obtener tamaño del archivo
        file_storage.seek(0, 2)  # Ir al final
        file_size = file_storage.tell()
        file_storage.seek(0)  # Volver al inicio

        # Validar tamaño
        if file_size > max_size:
            raise StorageUploadError(
                f"Archivo demasiado grande: {file_size} bytes. "
                f"Máximo permitido: {max_size} bytes"
            )

        if file_size == 0:
            raise StorageUploadError("El archivo está vacío")

        return content_type, file_size

    def _generate_filename(self, original_filename: str, folder: str = "sites") -> str:
        """Genera un nombre de archivo único y seguro"""
        # Sanitizar el nombre original
        safe_filename = Path(original_filename).name
        unique_id = uuid.uuid4().hex
        return f"{folder}/{unique_id}_{safe_filename}"

    def _get_base_url(self) -> str:
        """Obtiene la URL base del servidor MinIO"""
        protocol = "https" if self._secure else "http"
        return f"{protocol}://{self._endpoint}"

    @property
    def client(self):
        """Obtiene el cliente MinIO (solo para operaciones avanzadas)"""
        if not self._client:
            raise StorageConnectionError("Cliente MinIO no inicializado")
        return self._client

    @property
    def bucket_name(self) -> str:
        """Obtiene el nombre del bucket por defecto"""
        return self._bucket_name

    def upload_file(
            self,
            file_storage: FileStorage,
            bucket: Optional[str] = None,
            folder: str = "sites",
            validate: bool = True,
            public: bool = False,
            max_size: Optional[int] = None
    ) -> dict:
        """
        Sube un archivo a MinIO

        Args:
            file_storage: Objeto FileStorage de Flask/Werkzeug
            bucket: Nombre del bucket (usa el por defecto si es None)
            folder: Carpeta dentro del bucket
            validate: Si debe validar el archivo
            public: Si debe generar URL pública permanente
            max_size: Tamaño máximo permitido

        Returns:
            dict: Información del archivo subido {
                'url': URL del archivo,
                'key': Clave/path en el bucket,
                'bucket': Nombre del bucket,
                'size': Tamaño en bytes,
                'content_type': Tipo MIME
            }
        """
        if not self._client:
            raise StorageConnectionError("Cliente MinIO no inicializado")

        bucket = bucket or self._bucket_name

        try:
            # Validar archivo
            if validate:
                content_type, file_size = self._validate_file(file_storage, max_size)
            else:
                content_type = mimetypes.guess_type(file_storage.filename)[0] or "application/octet-stream"
                file_storage.seek(0, 2)
                file_size = file_storage.tell()
                file_storage.seek(0)

            # Generar nombre de archivo
            filename = self._generate_filename(file_storage.filename, folder)

            # Asegurar que el bucket existe
            self._ensure_bucket_exists(bucket)

            # Subir archivo
            self._client.put_object(
                bucket,
                filename,
                file_storage.stream,
                length=file_size,
                content_type=content_type,
            )

            self._logger.info(f"✓ Archivo subido: {bucket}/{filename} ({file_size} bytes)")

            # Generar URL
            if public:
                url = f"{self._get_base_url()}/{bucket}/{filename}"
            else:
                # URL pre-firmada con expiración
                url = self._client.presigned_get_object(
                    bucket,
                    filename,
                    expires=self.url_expiry
                )

            return {
                'url': url,
                'key': filename,
                'bucket': bucket,
                'size': file_size,
                'content_type': content_type
            }

        except StorageUploadError:
            raise  # Re-lanzar errores de validación
        except S3Error as e:
            self._logger.error(f"✗ Error S3 al subir archivo: {e}")
            raise StorageUploadError(f"Error al subir archivo: {e}")
        except Exception as e:
            self._logger.error(f"✗ Error inesperado al subir archivo: {e}")
            raise StorageUploadError(f"Error inesperado: {e}")

    def upload_bytes(
            self,
            data: bytes,
            filename: str,
            bucket: Optional[str] = None,
            folder: str = "sites",
            content_type: str = "application/octet-stream"
    ) -> dict:
        """
        Sube datos binarios directamente

        Args:
            data: Datos binarios a subir
            filename: Nombre del archivo
            bucket: Nombre del bucket
            folder: Carpeta dentro del bucket
            content_type: Tipo MIME

        Returns:
            dict: Información del archivo subido
        """
        if not self._client:
            raise StorageConnectionError("Cliente MinIO no inicializado")

        bucket = bucket or self._bucket_name

        try:
            file_key = self._generate_filename(filename, folder)
            file_size = len(data)

            self._ensure_bucket_exists(bucket)

            self._client.put_object(
                bucket,
                file_key,
                io.BytesIO(data),
                length=file_size,
                content_type=content_type,
            )

            self._logger.info(f"✓ Bytes subidos: {bucket}/{file_key} ({file_size} bytes)")

            url = self._client.presigned_get_object(bucket, file_key, expires=self.url_expiry)

            return {
                'url': url,
                'key': file_key,
                'bucket': bucket,
                'size': file_size,
                'content_type': content_type
            }

        except S3Error as e:
            raise StorageUploadError(f"Error al subir bytes: {e}")

    def delete_file(self, file_url: Optional[str] = None, key: Optional[str] = None,
                    bucket: Optional[str] = None) -> bool:
        """
        Elimina un archivo de MinIO

        Args:
            file_url: URL completa del archivo
            key: Clave/path del archivo en el bucket
            bucket: Nombre del bucket

        Returns:
            bool: True si se eliminó correctamente

        Note:
            Debes proporcionar file_url O (key + bucket)
        """
        if not self._client:
            raise StorageConnectionError("Cliente MinIO no inicializado")

        bucket = bucket or self._bucket_name

        try:
            # Extraer la key del URL si se proporcionó
            if file_url:
                # Remover query parameters (para URLs pre-firmadas)
                clean_url = file_url.split("?")[0]
                # Extraer bucket y key
                parts = clean_url.split(f"/{bucket}/")
                if len(parts) < 2:
                    raise StorageDeleteError(f"No se pudo extraer la key del URL: {file_url}")
                key = parts[1]

            if not key:
                raise StorageDeleteError("Debes proporcionar file_url o key")

            # Eliminar el archivo
            self._client.remove_object(bucket, key)
            self._logger.info(f"✓ Archivo eliminado: {bucket}/{key}")
            return True

        except S3Error as e:
            self._logger.error(f"✗ Error S3 al eliminar archivo: {e}")
            raise StorageDeleteError(f"Error al eliminar archivo: {e}")
        except Exception as e:
            self._logger.error(f"✗ Error inesperado al eliminar archivo: {e}")
            raise StorageDeleteError(f"Error inesperado: {e}")

    def file_exists(self, key: str, bucket: Optional[str] = None) -> bool:
        """Verifica si un archivo existe en el bucket"""
        if not self._client:
            raise StorageConnectionError("Cliente MinIO no inicializado")

        bucket = bucket or self._bucket_name

        try:
            self._client.stat_object(bucket, key)
            return True
        except S3Error:
            return False

    def get_file_info(self, key: str, bucket: Optional[str] = None) -> dict:
        """Obtiene información de un archivo"""
        if not self._client:
            raise StorageConnectionError("Cliente MinIO no inicializado")

        bucket = bucket or self._bucket_name

        try:
            stat = self._client.stat_object(bucket, key)
            return {
                'key': key,
                'bucket': bucket,
                'size': stat.size,
                'content_type': stat.content_type,
                'last_modified': stat.last_modified,
                'etag': stat.etag
            }
        except S3Error as e:
            raise StorageError(f"Error al obtener información del archivo: {e}")

    def get_presigned_url(self, key: str, bucket: Optional[str] = None, expires: Optional[timedelta] = None) -> str:
        """Genera una URL pre-firmada para un archivo existente"""
        if not self._client:
            raise StorageConnectionError("Cliente MinIO no inicializado")

        bucket = bucket or self._bucket_name
        expires = expires or self.url_expiry

        try:
            return self._client.presigned_get_object(bucket, key, expires=expires)
        except S3Error as e:
            raise StorageError(f"Error al generar URL pre-firmada: {e}")

    def list_files(self, bucket: Optional[str] = None, prefix: str = "", recursive: bool = True) -> list:
        """Lista archivos en un bucket"""
        if not self._client:
            raise StorageConnectionError("Cliente MinIO no inicializado")

        bucket = bucket or self._bucket_name

        try:
            objects = self._client.list_objects(bucket, prefix=prefix, recursive=recursive)
            return [
                {
                    'key': obj.object_name,
                    'size': obj.size,
                    'last_modified': obj.last_modified,
                    'etag': obj.etag
                }
                for obj in objects
            ]
        except S3Error as e:
            raise StorageError(f"Error al listar archivos: {e}")


# Instancia global
storage = Storage()