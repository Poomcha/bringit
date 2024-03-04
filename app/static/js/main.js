import { auth } from "./auth.js";
import { profile } from "./profile.js";

window.addEventListener("DOMContentLoaded", () => {
  auth();
  profile();
});
