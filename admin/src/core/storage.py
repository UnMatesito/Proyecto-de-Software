import json
import logging
import mimetypes
import uuid
from pathlib import Path
from typing import Optional

from minio import Minio
from minio.error import S3Error
from werkzeug.datastructures import FileStorage


class StorageError(Exception):
    """Excepción base para errores de Storage"""

    pass


class Storage:
    """
    Cliente MinIO simplificado para almacenamiento de imágenes públicas.
    Características:
    - Crea automáticamente el bucket si no existe
    - Configura el bucket como público
    - Genera nombres únicos para archivos
    - Retorna URLs públicas directas
    """

    # Límites
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

    # Tipos MIME permitidos para imágenes
    ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}

    def __init__(self, app=None):
        self._client = None
        self._bucket_name = None
        self._endpoint = None
        self._secure = False
        self._logger = logging.getLogger(__name__)

        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """Inicializa el cliente MinIO con la aplicación Flask"""
        endpoint = app.config.get(
            "MINIO_SERVER", "https://minio.proyecto2025.linti.unlp.edu.ar/"
        )
        access_key = app.config.get("MINIO_ACCESS_KEY", "minioadmin")
        secret_key = app.config.get("MINIO_SECRET_KEY", "minioadmin")
        self._secure = app.config.get("MINIO_SECURE", False)
        self._bucket_name = app.config.get("MINIO_BUCKET", "grupo09")
        self._logger = app.logger

        # Limpiar el endpoint
        self._endpoint = endpoint.replace("http://", "").replace("https://", "")

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

            # Crear bucket público si no existe
            self._setup_public_bucket()

        except Exception as e:
            self._logger.error(f"✗ Error al inicializar MinIO: {e}")
            raise StorageError(f"Error de inicialización: {e}")

        app.storage = self
        return app

    def _setup_public_bucket(self):
        """Crea el bucket y lo configura como público"""
        try:
            # Crear bucket si no existe
            if not self._client.bucket_exists(self._bucket_name):
                self._client.make_bucket(self._bucket_name)
                self._logger.info(f"✓ Bucket creado: {self._bucket_name}")

            # Configurar como público
            policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {"AWS": "*"},
                        "Action": ["s3:GetObject"],
                        "Resource": [f"arn:aws:s3:::{self._bucket_name}/*"],
                    }
                ],
            }

            self._client.set_bucket_policy(self._bucket_name, json.dumps(policy))
            self._logger.info(f"✓ Bucket configurado como público: {self._bucket_name}")

        except S3Error as e:
            raise StorageError(f"Error al configurar bucket: {e}")

    def _validate_image(self, file: FileStorage) -> tuple[str, int]:
        """Valida que el archivo sea una imagen válida"""
        # Obtener tipo MIME
        content_type = mimetypes.guess_type(file.filename)[0]
        if not content_type:
            content_type = file.content_type or "application/octet-stream"

        # Validar tipo MIME
        if content_type not in self.ALLOWED_MIME_TYPES:
            raise StorageError(
                f"Tipo de archivo no permitido: {content_type}. "
                f"Solo se permiten imágenes: {', '.join(self.ALLOWED_MIME_TYPES)}"
            )

        # Obtener tamaño
        file.seek(0, 2)
        file_size = file.tell()
        file.seek(0)

        # Validar tamaño
        if file_size == 0:
            raise StorageError("El archivo está vacío")

        if file_size > self.MAX_FILE_SIZE:
            raise StorageError(
                f"Archivo demasiado grande: {file_size / 1024 / 1024:.2f}MB. "
                f"Máximo: {self.MAX_FILE_SIZE / 1024 / 1024}MB"
            )

        return content_type, file_size

    def _generate_filename(self, original_filename: str, folder: str = "sites") -> str:
        """Genera un nombre único y seguro para el archivo"""
        safe_filename = Path(original_filename).name
        unique_id = uuid.uuid4().hex[:12]  # 12 caracteres son suficientes
        extension = Path(safe_filename).suffix
        return f"{folder}/{unique_id}{extension}"

    def _get_public_url(self, key: str) -> str:
        """Genera la URL pública del archivo"""
        protocol = "https" if self._secure else "http"
        return f"{protocol}://{self._endpoint}/{self._bucket_name}/{key}"

    def upload_file(
        self,
        file_storage: FileStorage,
        folder: str = "sites",
        validate: bool = True,
        public: bool = True,
    ) -> dict:
        """
        Sube una imagen a MinIO y retorna su URL pública.

        Args:
            file_storage: Archivo de imagen (FileStorage)
            folder: Carpeta dentro del bucket (default: "sites")
            validate: Si debe validar el archivo (default: True)
            public: Mantiene compatibilidad, siempre retorna URL pública

        Returns:
            dict: {
                'url': URL pública del archivo,
                'key': Ruta del archivo en el bucket,
                'size': Tamaño en bytes,
                'content_type': Tipo MIME
            }
        """
        if not self._client:
            raise StorageError("Cliente MinIO no inicializado")

        try:
            # Validar imagen si está habilitado
            if validate:
                content_type, file_size = self._validate_image(file_storage)
            else:
                content_type = (
                    mimetypes.guess_type(file_storage.filename)[0]
                    or "application/octet-stream"
                )
                file_storage.seek(0, 2)
                file_size = file_storage.tell()
                file_storage.seek(0)

            # Generar nombre único
            file_key = self._generate_filename(file_storage.filename, folder)

            # Subir archivo
            self._client.put_object(
                self._bucket_name,
                file_key,
                file_storage.stream,
                length=file_size,
                content_type=content_type,
            )

            self._logger.info(f"✓ Imagen subida: {file_key} ({file_size} bytes)")

            # Retornar información con URL pública
            return {
                "url": self._get_public_url(file_key),
                "key": file_key,
                "size": file_size,
                "content_type": content_type,
            }

        except StorageError:
            raise
        except S3Error as e:
            self._logger.error(f"✗ Error S3: {e}")
            raise StorageError(f"Error al subir imagen: {e}")
        except Exception as e:
            self._logger.error(f"✗ Error inesperado: {e}")
            raise StorageError(f"Error inesperado: {e}")

    def delete_file(
        self, file_url: Optional[str] = None, key: Optional[str] = None
    ) -> bool:
        """
        Elimina una imagen de MinIO.

        Args:
            file_url: URL completa del archivo
            key: Ruta del archivo en el bucket

        Returns:
            bool: True si se eliminó correctamente

        Note:
            Proporciona file_url O key (al menos uno)
        """
        if not self._client:
            raise StorageError("Cliente MinIO no inicializado")

        try:
            # Extraer key de la URL si se proporcionó
            if file_url and not key:
                parts = file_url.split(f"/{self._bucket_name}/")
                if len(parts) < 2:
                    raise StorageError(f"URL inválida: {file_url}")
                key = parts[1].split("?")[0]  # Remover query params si existen

            if not key:
                raise StorageError("Debes proporcionar file_url o key")

            # Eliminar archivo
            self._client.remove_object(self._bucket_name, key)
            self._logger.info(f"✓ Imagen eliminada: {key}")
            return True

        except S3Error as e:
            self._logger.error(f"✗ Error S3: {e}")
            raise StorageError(f"Error al eliminar imagen: {e}")
        except Exception as e:
            self._logger.error(f"✗ Error inesperado: {e}")
            raise StorageError(f"Error inesperado: {e}")

    def image_exists(self, key: str) -> bool:
        """Verifica si una imagen existe en el bucket"""
        if not self._client:
            raise StorageError("Cliente MinIO no inicializado")

        try:
            self._client.stat_object(self._bucket_name, key)
            return True
        except S3Error:
            return False

    def get_image_info(self, key: str) -> dict:
        """Obtiene información de una imagen"""
        if not self._client:
            raise StorageError("Cliente MinIO no inicializado")

        try:
            stat = self._client.stat_object(self._bucket_name, key)
            return {
                "key": key,
                "url": self._get_public_url(key),
                "size": stat.size,
                "content_type": stat.content_type,
                "last_modified": stat.last_modified,
            }
        except S3Error as e:
            raise StorageError(f"Error al obtener información: {e}")

    @property
    def bucket_name(self) -> str:
        """Retorna el nombre del bucket"""
        return self._bucket_name


# Instancia global
storage = Storage()
