import api from "@/api/axios.js";

export const getFeatureFlag = async (name) => {
  const res = await api.get(`/feature-flags/${name}`)

  return res.data;
};
