function profile() {
  const url_path = window.location.pathname;
  if (url_path === "/profile/") {
    handleAvatarPreview();
    handleModify();
  }
  return;
}

const handleAvatarPreview = () => {
  const image_input = document.querySelector("#avatar-profile");
  const image_preview = document.querySelector("#profile-picture");

  const handleImage = (event) => {
    event.preventDefault();

    const image = image_input.files[0];
    if (!image.type.startsWith("image/")) return;

    image_preview.file = image;

    const reader = new FileReader();
    reader.onload = (e) => {
      image_preview.src = e.target.result;
    };
    reader.readAsDataURL(image);
  };

  image_input.addEventListener("change", handleImage);
  return;
};

const handleModify = () => {
  const modify_infos = document.querySelector("#modify-infos");
  const modify_password = document.querySelector("#modify-password");

  const modify = (event) => {
    event.preventDefault();

    if (event.target === modify_infos) {
      const save_infos = document.querySelector("#save-infos");
      save_infos.disabled = false;

      const inputs_infos = document.querySelectorAll(".input-infos");
      inputs_infos.forEach((input) => (input.disabled = false));
    }

    if (event.target === modify_password) {
      const save_password = document.querySelector("#save-password");
      save_password.disabled = false;

      const inputs_password = document.querySelectorAll(".input-password");
      inputs_password.forEach((input) => (input.disabled = false));
    }
  };

  [modify_infos, modify_password].forEach((modifier) =>
    modifier.addEventListener("click", modify)
  );
};

export { profile };
