const url_path = window.location.pathname;
const form_item_init =
  url_path === "/lists/create"
    ? document.querySelector(".item-root[data-bgit='item-form-0']")
    : undefined;
const form_item_bp =
  url_path === "/lists/create" ? form_item_init.cloneNode(true) : undefined;

function lists() {
  if (url_path === "/lists/create") {
    const add_item_btn = document.querySelector(".add-item");
    add_item_btn.addEventListener("click", handleAddItem);

    handleItem(form_item_init);

    const form = document.querySelector("#listform");
    form.addEventListener("submit", handleSubmit);

    return;
  }
  function handleAddItem(event) {
    event.preventDefault();

    const form_item_new = form_item_bp.cloneNode(true);
    const form_item_list = document.querySelector("#item-list");
    const form_item_number = document.querySelectorAll(".item-form").length;

    form_item_new.dataset["bgit"] = `item-form-${form_item_number}`;
    form_item_new
      .querySelectorAll("[data-bgit='item-form-0']")
      .forEach((element) =>
        element.setAttribute("data-bgit", `item-form-${form_item_number}`)
      );

    handleItem(form_item_list.appendChild(form_item_new));
  }
}

function handleItem(form_item) {
  const form_item_id = form_item.dataset["bgit"].split("-")[2];

  const remove_btns = form_item.querySelectorAll(".remove-item");
  remove_btns.forEach((btn) => btn.addEventListener("click", handleRemoveItem));

  const validate_btn = form_item.querySelector(".validate-item");
  validate_btn.addEventListener("click", handleValidateItem);

  const modify_btn = form_item.querySelector(".modify-item");
  modify_btn.addEventListener("click", handleModifyItem);

  const inputs_list = form_item.querySelectorAll(".item-inputs-list > li");
  inputs_list.forEach((li) => {
    li.classList.add("d-flex", "flex-column");
    li.childNodes[0].classList.add("form-label", "text-light");
    li.childNodes[2].classList.add("form-control");
    li.childNodes[2].setAttribute("data-bgit", `item-form-${form_item_id}`);
  });
  return form_item;
}

function handleRemoveItem(event) {
  event.preventDefault();

  const item_id = event.target.dataset["bgit"];

  document.querySelector(`.item-root[data-bgit='${item_id}']`).remove();
  return;
}

function handleValidateItem(event) {
  event.preventDefault();

  handleItemPreview(event.target);

  const item_id = event.target.dataset["bgit"];
  const item_form = document.querySelector(
    `.item-form[data-bgit='${item_id}']`
  );
  const item_card = document.querySelector(`.card[data-bgit='${item_id}']`);
  item_form.hidden = true;
  item_card.hidden = false;

  return;
}

function handleItemPreview(item) {
  const item_id = item.dataset["bgit"];

  // Handles image preview
  const image_input = document.querySelector(
    `#itemform-item_image[data-bgit='${item_id}']`
  );
  const image_preview = document.querySelector(
    `.item-image[data-bgit='${item_id}']`
  );

  const handleImage = () => {
    const image = image_input.files[0];
    if (!image) return;
    if (!image.type.startsWith("image/")) return;

    image_preview.file = image;

    const reader = new FileReader();
    reader.onload = (e) => {
      image_preview.src = e.target.result;
    };
    reader.readAsDataURL(image);
  };

  handleImage();

  // Handles title preview
  const title_input = document.querySelector(
    `#itemform-item_title[data-bgit='${item_id}']`
  );
  const title_preview = document.querySelector(
    `.card-title[data-bgit='${item_id}']`
  );

  title_preview.innerHTML = `${title_input.value}`;

  return;
}

function handleModifyItem(event) {
  event.preventDefault();

  const item_id = event.target.dataset["bgit"];
  const item_form = document.querySelector(
    `.item-form[data-bgit='${item_id}']`
  );
  const item_card = document.querySelector(`.card[data-bgit='${item_id}']`);
  item_form.hidden = false;
  item_card.hidden = true;

  return;
}

function handleSubmit(event) {
  // Rename fields name and id for each items
  const item_roots = event.target.querySelectorAll(".item-root");
  item_roots.forEach((root) => {
    const root_number = parseInt(root.dataset["bgit"].split("-")[2]);
    root.querySelectorAll("[id^='itemform-item']").forEach((input) => {
      input.id = `${input.id}-${root_number}`;
      input.name = `${input.id}`;
    });
  });
}

export { lists };
