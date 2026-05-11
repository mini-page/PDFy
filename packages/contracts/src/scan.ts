import { z } from "zod";

export const retentionModeSchema = z.enum([
  "delete_immediately",
  "temporary_cache"
]);

export const createScanInputSchema = z.object({
  retentionMode: retentionModeSchema.default("delete_immediately"),
  enableEnrichment: z.boolean().default(true)
});

export const scanStatusSchema = z.enum([
  "queued_fast_scan",
  "running_fast_scan",
  "completed_fast_scan",
  "queued_advanced_scan",
  "running_advanced_scan",
  "completed",
  "failed",
  "expired"
]);
