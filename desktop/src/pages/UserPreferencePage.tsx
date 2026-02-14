import { UserPreferenceManager } from "./UserPreferences/UserPreferenceManager";

/**
 * UserPreferencePage - Main page wrapper for user preferences
 * This component is automatically picked up by the router
 */
function UserPreferencePage() {
  return <UserPreferenceManager />;
}

export default UserPreferencePage;
