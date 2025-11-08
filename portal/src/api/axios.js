import axios from "axios";

// instancia principal para el resto del proyecto
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://127.0.0.1:5000/api",
  withCredentials: true,
});

export default api;

// funciones específicas para reseñas
export const getReviewsBySite = async (siteId) => {
  const res = await api.get(`/sites/${siteId}/reviews`);
  console.log(res.data)
  return res.data;
};

export const createReview = async (siteId, review) => {
  const res = await api.post(
    `/sites/${siteId}/reviews`,
    {
      rating: review.rating,
      comment: review.text,
    },
  );
  return res.data;
};
//CREO QUE NO SE PUEDE EDITAR UNA REVIEW
/*export const updateReview = async (siteId, reviewId, review) => {
  const res = await api.put(
    `/sites/${siteId}/reviews/${reviewId}`,
    {
      rating: review.rating,
      comment: review.text,
    },
  );
  return res.data;
};*/

export const deleteReview = async (siteId, reviewId) => {
  await api.delete(`/sites/${siteId}/reviews/${reviewId}`, {
  });
};
