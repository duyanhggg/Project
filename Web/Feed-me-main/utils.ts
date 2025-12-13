import { UserProfile, DEFAULT_PROFILE } from "./types";

/**
 * Encodes the profile object to a Base64 string for the URL.
 * This allows sharing the page without a backend database.
 */
export const encodeProfileData = (data: UserProfile): string => {
  try {
    const jsonString = JSON.stringify(data);
    return btoa(encodeURIComponent(jsonString));
  } catch (e) {
    console.error("Error encoding data", e);
    return "";
  }
};

/**
 * Decodes the Base64 string from URL back to a profile object.
 */
export const decodeProfileData = (encoded: string | null): UserProfile => {
  if (!encoded) return DEFAULT_PROFILE;
  try {
    const jsonString = decodeURIComponent(atob(encoded));
    return JSON.parse(jsonString);
  } catch (e) {
    console.error("Error decoding data", e);
    return DEFAULT_PROFILE;
  }
};