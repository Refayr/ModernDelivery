//-------------------------------------
// Document options
//
#let option = (
  //type : "final",
  type: "draft",
  lang: "en",
  //lang : "de",
  //lang : "fr",
)
//-------------------------------------
// Optional generate titlepage image
//
#import "@preview/fractusist:0.1.1": *
// only for the generated images

#let titlepage_logo = dragon-curve(
  12,
  step-size: 10,
  stroke-style: stroke(
    //paint: gradient.linear(..color.map.rocket, angle: 135deg),
    //paint: gradient.radial(..color.map.rocket),
    paint: gradient.radial(..color.map.mako),
    thickness: 3pt,
    join: "round",
  ),
  height: 10cm,
)

/*#let titlepage_logo = lsystem(
  ..lsystem-use("Gosper Curve"),
  order: 4,
  step-size: 3,
  start-angle: 0,
  stroke: stroke(
    paint: gradient.linear(purple, blue, angle: 60deg),
    thickness: 1.5pt,
    cap: "round",
    join: "round"
  )
)*/

//------------------------------------
// Metadata of the document
//
#let doc = (
  title: [*The Art and Science of Modern Delivery: From Factory to Final Mile*],
  //abbr: "Prj",
  subtitle: [_PostgreSQL Project_],
  url: "https://github.com/Refayr/ModernDelivery",
  logos: (
    tp_topleft: image("resources/img/ipparis.jpg", height: 1.2cm),
    tp_topright: image("resources/img/polytechnique.jpg", height: 1.5cm),
    tp_main: titlepage_logo,
    header: image("resources/img/modern_delivery.jpg", width: 2.5cm),
  ),
  authors: (
    (
      name: "Katerina Michenina",
      abbr: "KM",
      email: "katerina.michenina@polytechnique.edu",
      //url: "https://synd.hevs.io",
    ),
    (
      name: "Aya Matmata",
      abbr: "AM",
      email: "aya.matmata@polytechnique.edu",
      //url: "https://synd.hevs.io",
    ),
    (
      name: "Nicolas Valety",
      abbr: "NV",
      email: "nicolas.valety@ip-paris.fr",
      url: "https://github.com/Refayr/ModernDelivery",
    ),
  ),
  school: (
    name: "Polytechnique Institute of Paris",
    major: "Applied Mathematics and Statistics",
    orientation: "Master degree",
    url: "https://www.polytechnique.edu/",
  ),
  course: (
    name: "Database Management Systems",
    url: "https://www.polytechnique.edu/annuaire/gaur-garima",
    prof: "Garima Gaur",
    class: [M1 APPMS],
    semester: "Winter Semester 2026",
  ),
  keywords: ("Typst", "Template", "Report", "HEI-Vs", "Project", "Logistics", "Delivery", "Drone"),
  version: "v0.1.0",
)

#let date = datetime.today()

//-------------------------------------
// Settings
//
#let tableof = (
  toc: true,
  tof: false,
  tot: false,
  tol: false,
  toe: false,
  maxdepth: 3,
)

#let gloss = true
#let appendix = false
#let bib = (
  display: true,
  path: "/tail/bibliography.bib",
  style: "ieee",
  //"apa", "chicago-author-date", "chicago-notes", "mla"
)
