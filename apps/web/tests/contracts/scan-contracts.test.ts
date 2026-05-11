import { describe, expect, it } from "vitest";

import { createScanInputSchema, retentionModeSchema } from "@pdfy/contracts";

describe("scan contracts", () => {
  it("defaults upload requests to immediate deletion", () => {
    const parsed = createScanInputSchema.parse({});

    expect(parsed.retentionMode).toBe("delete_immediately");
  });

  it("allows only supported retention modes", () => {
    expect(retentionModeSchema.safeParse("temporary_cache").success).toBe(true);
    expect(retentionModeSchema.safeParse("forever").success).toBe(false);
  });
});
