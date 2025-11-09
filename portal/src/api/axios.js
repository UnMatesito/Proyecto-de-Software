import axios from "axios";


function getCookie(name) {
  /* Rescata la cookie la uso para mediante otra funcion mandar el csrf token para operaciones de tipo post put delete */
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
}

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://127.0.0.1:5000/api",
  withCredentials: true,
  xsrfCookieName: "csrf_access_token",
  xsrfHeaderName: "X-CSRF-TOKEN",
});

api.interceptors.request.use((config) => {
  const csrfToken = getCookie("csrf_access_token");
  if (csrfToken && ["post", "put", "patch", "delete"].includes(config.method)) {
    config.headers["X-CSRF-TOKEN"] = csrfToken;
  }
  return config;
});

export default api;

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

export const deleteReview = async (siteId, reviewId) => {
  await api.delete(`/sites/${siteId}/reviews/${reviewId}`, {
  });
};
