function updateValue(slider) {
  const valueSpan = slider.nextElementSibling;
  valueSpan.textContent = parseFloat(slider.value).toFixed(1);
}