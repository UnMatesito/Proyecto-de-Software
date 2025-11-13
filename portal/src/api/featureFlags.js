const cache = {};
const ongoing = {};

export const getFeatureFlag = async (name) => {
  // Si ya está en caché, devolverla sin llamar a la API
  if (cache[name]) return cache[name];

  // Si ya se está pidiendo, devolver la misma promesa
  if (ongoing[name]) return ongoing[name];

  // Si no existe en caché ni hay request en curso, pedirla
  ongoing[name] = api.get(`/feature-flags/${name}`)
    .then((res) => {
      cache[name] = res.data;
      return cache[name];
    })
    .finally(() => {
      delete ongoing[name];
    });

  return ongoing[name];
};
