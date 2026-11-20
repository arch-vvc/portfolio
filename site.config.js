// Everything Bob fills in later. Empty means "not shown".
// Loaded with a plain script tag, so it works when index.html is opened from disk.
var SITE_CONFIG = {
  // Loom video URL per project. An empty string means no demo button.
  demos: {
    callqa: "",
    triage: "",
    gtm: "",
    tender: "",
    capstone: ""
  },
  // Optional phone number. When set, the Phone app on the phone layout gets a Call row. Left empty on purpose.
  phone: "",
  // Safari tabs. An empty value leaves that tab as a stub.
  twitter: "",
  youtube: "",
  // Path to the screenshot shown in the Krillion tab, for example "assets/krillion.png".
  krillionImage: "",
  // Call QA live result text, shown on the project page when not empty.
  callqaResult: "",
  // Capstone result text, shown under Research when not empty.
  capstoneResult: "",
  // Path to the CV PDF, for example "assets/archit-rishabh-cv.pdf". Empty hides the CV button.
  cvPath: "assets/Archit_Rishabh_CV.pdf",
  // Windstream photos, for example { src: "assets/site-1.jpg", caption: "Site survey", alt: "..." }.
  windstreamPhotos: [],
  // Exact degree title. Until set, the site shows "AI and ML engineering".
  degreeTitle: ""
};
