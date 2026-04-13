import { http } from "./http";

export const api = {
  register: (payload: { username: string; password: string }) =>
    http.post("/auth/register", payload),
  login: (payload: { username: string; password: string }) =>
    http.post("/auth/login", payload),
  me: () => http.get("/auth/me"),
  courses: () => http.get("/courses"),
  kps: (courseId: number) => http.get("/kps", { params: { course_id: courseId } }),
  createKp: (payload: any) => http.post("/kps", payload),
  updateKp: (id: number, payload: any) => http.put(`/kps/${id}`, payload),
  deleteKp: (id: number) => http.delete(`/kps/${id}`),
  prereqs: (courseId: number) => http.get("/prereqs", { params: { course_id: courseId } }),
  createPrereq: (payload: any) => http.post("/prereqs", payload),
  deletePrereq: (id: number) => http.delete(`/prereqs/${id}`),
  resources: (kpId: number) => http.get("/resources", { params: { kp_id: kpId } }),
  createResource: (payload: any) => http.post("/resources", payload),
  updateResource: (id: number, payload: any) => http.put(`/resources/${id}`, payload),
  deleteResource: (id: number) => http.delete(`/resources/${id}`),
  assessments: (kpId: number) => http.get("/assessments", { params: { kp_id: kpId } }),
  createAssessment: (payload: any) => http.post("/assessments", payload),
  createRecord: (payload: any) => http.post("/assessment_records", payload),
  createEvent: (payload: any) => http.post("/learning_events", payload),
  mastery: (courseId: number, userId?: number) =>
    http.get("/mastery", { params: { course_id: courseId, user_id: userId } }),
  generatePath: (payload: any) => http.post("/paths/generate", payload),
  latestPath: (courseId: number) => http.get("/paths/latest", { params: { course_id: courseId } }),
  getPath: (id: number) => http.get(`/paths/${id}`),
  getStrategy: (courseId: number) => http.get("/strategy", { params: { course_id: courseId } }),
  updateStrategy: (payload: any) => http.put("/strategy", payload),
  stats: (courseId: number) => http.get("/stats", { params: { course_id: courseId } }),
  users: () => http.get("/users"),
  updateUser: (id: number, payload: any) => http.put(`/users/${id}`, payload),
  exportEvents: (courseId: number) =>
    http.get("/export/events", { params: { course_id: courseId }, responseType: "blob" }),
  exportRecords: (courseId: number) =>
    http.get("/export/records", { params: { course_id: courseId }, responseType: "blob" }),
  exportMastery: (courseId: number) =>
    http.get("/export/mastery", { params: { course_id: courseId }, responseType: "blob" }),
  exportPaths: (courseId: number) =>
    http.get("/export/paths", { params: { course_id: courseId }, responseType: "blob" })
};
