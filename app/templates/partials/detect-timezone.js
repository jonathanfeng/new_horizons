(function () {
  var root = document.documentElement;
  var mode = root.getAttribute("data-tz-detect");
  var zone;
  try {
    zone = Intl.DateTimeFormat().resolvedOptions().timeZone;
  } catch (error) {
    return;
  }
  if (!mode || !zone) return;
  document.cookie = "cc_timezone=" + zone + "; Max-Age=31536000; Path=/; SameSite=Lax";
  if (mode === "verify" && Number(root.getAttribute("data-tz-offset")) === -new Date().getTimezoneOffset()) return;
  try {
    if (sessionStorage.getItem("cc-tz-detected") === zone) return;
    sessionStorage.setItem("cc-tz-detected", zone);
  } catch (error) {
    return;
  }
  root.classList.add("is-detecting");
  if (document.cookie.indexOf("cc_timezone=") !== -1) {
    location.reload();
  } else {
    var url = new URL(location.href);
    url.searchParams.set("timezone", zone);
    location.replace(url.toString());
  }
})();
