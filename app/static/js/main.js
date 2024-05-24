import { auth } from "./auth.js";
import { profile } from "./profile.js";
import { lists } from "./lists.js";

window.addEventListener("DOMContentLoaded", () => {
  auth();
  profile();
  lists();
});
