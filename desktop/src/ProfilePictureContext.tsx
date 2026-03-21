import { createContext, useContext, useState, useEffect, useCallback, type ReactNode } from "react";
import { getUserPreferences, getProfilePictureUrl } from "./api/userPreferences";

interface ProfilePictureContextValue {
  /** The URL to use as <img src> — either the API endpoint URL or null if no picture is set */
  profilePicture: string | null;
  refreshProfilePicture: () => Promise<void>;
  setProfilePicture: (url: string | null) => void;
}

const ProfilePictureContext = createContext<ProfilePictureContextValue>({
  profilePicture: null,
  refreshProfilePicture: async () => {},
  setProfilePicture: () => {},
});

export function ProfilePictureProvider({ children }: { children: ReactNode }) {
  const [profilePicture, setProfilePicture] = useState<string | null>(null);

  const refreshProfilePicture = useCallback(async () => {
    try {
      const prefs = await getUserPreferences();
      // If the DB has a path stored, use the dedicated API endpoint as the img src.
      // Adding a cache-busting timestamp ensures the browser re-fetches after an upload.
      if (prefs.profile_picture) {
        setProfilePicture(`${getProfilePictureUrl()}?t=${Date.now()}`);
      } else {
        setProfilePicture(null);
      }
    } catch {
      setProfilePicture(null);
    }
  }, []);

  useEffect(() => {
    refreshProfilePicture();
  }, [refreshProfilePicture]);

  return (
    <ProfilePictureContext.Provider value={{ profilePicture, refreshProfilePicture, setProfilePicture }}>
      {children}
    </ProfilePictureContext.Provider>
  );
}

export function useProfilePicture() {
  return useContext(ProfilePictureContext);
}
