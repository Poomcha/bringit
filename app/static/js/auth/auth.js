function auth() {
  const url_path = window.location.pathname;
  if (url_path === "/auth/") {
    const link_signin = document.querySelector("#link-signin");
    const link_signup = document.querySelector("#link-signup");

    const tabpanel_signin = document.querySelector("#tabpanel-signin");
    const tabpanel_signup = document.querySelector("#tabpanel-signup");

    const handleTabs = (event) => {
      event.preventDefault();
      if (event.target.id === "link-signin") {
        link_signin.classList.add("active");
        link_signup.classList.remove("active");
        tabpanel_signin.classList.add("show", "active");
        tabpanel_signup.classList.remove("show", "active");
      }
      if (event.target.id === "link-signup") {
        link_signin.classList.remove("active");
        link_signup.classList.add("active");
        tabpanel_signin.classList.remove("show", "active");
        tabpanel_signup.classList.add("show", "active");
      }
    };

    [link_signin, link_signup].forEach((link) =>
      link.addEventListener("click", handleTabs)
    );
  }
  return;
}

export { auth };
