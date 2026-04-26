import { ShortlistResponse } from "../types";

export async function buildShortlist(rawDescription: string): Promise<ShortlistResponse> {
  const response = await fetch("/jobs/shortlist", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      raw_description: rawDescription,
      limit: 6
    })
  });

  if (!response.ok) {
    throw new Error("Unable to build shortlist.");
  }

  return (await response.json()) as ShortlistResponse;
}
