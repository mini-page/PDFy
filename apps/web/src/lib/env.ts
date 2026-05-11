import { z } from "zod";

export const envSchema = z.object({
  DATABASE_URL: z.string().url(),
  ANALYZER_BASE_URL: z.string().url(),
  REDIS_URL: z.string().url(),
  S3_ENDPOINT: z.string().url()
});
