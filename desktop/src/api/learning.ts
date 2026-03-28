import { API_BASE_URL } from "../config/api";

const API_BASE = API_BASE_URL;

export type CoursePricing = "free" | "paid";
export type CourseLevel = "starter" | "advanced";

export interface LearningCourse {
  id: string;
  title: string;
  description: string;
  url: string;
  thumbnail_url: string;
  provider: string;
  tags: string[];
  level: CourseLevel;
  pricing: CoursePricing;
}

export interface LearningRecommendationsResponse {
  based_on_resume: LearningCourse[];
  next_steps: LearningCourse[];
}

export async function getLearningRecommendations(): Promise<LearningRecommendationsResponse> {
  const url = `${API_BASE}/api/learning/recommendations`;
  let res: Response;
  try {
    res = await fetch(url, { method: "GET" });
  } catch (e) {
    if (e instanceof TypeError) {
      throw new Error(
        `Cannot reach the API at ${API_BASE} (${url}). ` +
          "Start the FastAPI server (e.g. on port 8000), or set VITE_API_BASE_URL in .env to match where it runs."
      );
    }
    throw e;
  }
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    if (res.status === 404) {
      throw new Error(
        "Learning recommendations endpoint returned 404. " +
          "Set VITE_API_BASE_URL to the API origin only (e.g. http://127.0.0.1:8000), not …/api. " +
          "Restart the FastAPI app from the latest project code so GET /api/learning/recommendations is registered. " +
          (text ? `(${text})` : "")
      );
    }
    throw new Error(text || `Failed to load learning recommendations (${res.status})`);
  }
  return res.json() as Promise<LearningRecommendationsResponse>;
}

/** Resolve catalog thumbnail URLs that are app-relative (e.g. /static/learning/...). */
export function learningThumbnailSrc(thumbnailUrl: string): string {
  if (!thumbnailUrl) return "";
  if (thumbnailUrl.startsWith("/")) {
    return `${API_BASE}${thumbnailUrl}`;
  }
  return thumbnailUrl;
}
