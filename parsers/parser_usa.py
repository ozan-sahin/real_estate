#%%
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

def parse() -> pd.DataFrame:

    us_data = {
        "Alabama": {"code": "AL", "counties": {
            "Autauga County": 119, "Baldwin County": 120, "Barbour County": 121, "Bibb County": 122,
            "Blount County": 123, "Bullock County": 124, "Butler County": 125, "Calhoun County": 126,
            "Chambers County": 127, "Cherokee County": 128, "Chilton County": 129, "Choctaw County": 130,
            "Clarke County": 131, "Clay County": 132, "Cleburne County": 133, "Coffee County": 134,
            "Colbert County": 135, "Conecuh County": 136, "Coosa County": 137, "Covington County": 138,
            "Crenshaw County": 139, "Cullman County": 140, "Dale County": 141, "Dallas County": 142,
            "DeKalb County": 143, "Elmore County": 144, "Escambia County": 145, "Etowah County": 146,
            "Fayette County": 147, "Franklin County": 148, "Geneva County": 149, "Greene County": 150,
            "Hale County": 151, "Henry County": 152, "Houston County": 153, "Jackson County": 154,
            "Jefferson County": 155, "Lamar County": 156, "Lauderdale County": 157, "Lawrence County": 158,
            "Lee County": 159, "Limestone County": 160, "Lowndes County": 161, "Macon County": 162,
            "Madison County": 163, "Marengo County": 164, "Marion County": 165, "Marshall County": 166,
            "Mobile County": 167, "Monroe County": 168, "Montgomery County": 169, "Morgan County": 170,
            "Perry County": 171, "Pickens County": 172, "Pike County": 173, "Randolph County": 174,
            "Russell County": 175, "Shelby County": 177, "St. Clair County": 176, "Sumter County": 178,
            "Talladega County": 179, "Tallapoosa County": 180, "Tuscaloosa County": 181, "Walker County": 182,
            "Washington County": 183, "Wilcox County": 184, "Winston County": 185,
        }},
        "Alaska": {"code": "AK", "counties": {
        "Aleutians East Borough": 186, "Aleutians West Census Area": 187, "Anchorage Borough": 188,
        "Bethel Census Area": 189, "Bristol Bay Borough": 190, "Denali Borough": 191,
        "Dillingham Census Area": 192, "Fairbanks North Star Borough": 193, "Haines Borough": 194,
        "Hoonah Angoon Census Area": 3351, "Juneau Borough": 195, "Kenai Peninsula Borough": 196,
        "Ketchikan Gateway Borough": 197, "Kodiak Island Borough": 198, "Kusilvak Census Area": 209,
        "Lake and Peninsula Borough": 199, "Matanuska Susitna Borough": 200, "Nome Census Area": 201,
        "North Slope Borough": 202, "Northwest Arctic Borough": 203, "Petersburg Borough": 3352,
        "Prince of Wales Hyder Census Area": 204, "Sitka Borough": 205, "Skagway Borough": 206,
        "Southeast Fairbanks Census Area": 207, "Valdez Cordova Census Area": 208,
        "Wrangell Borough": 210, "Yakutat Borough": 211, "Yukon Koyukuk Census Area": 212,
        }},
        "Arizona": {"code": "AZ", "counties": {
            "Apache County": 213, "Cochise County": 214, "Coconino County": 215, "Gila County": 216,
            "Graham County": 217, "Greenlee County": 218, "La Paz County": 219, "Maricopa County": 220,
            "Mohave County": 221, "Navajo County": 222, "Pima County": 223, "Pinal County": 224,
            "Santa Cruz County": 225, "Yavapai County": 226, "Yuma County": 227,
        }},
        "Arkansas": {"code": "AR", "counties": {
            "Arkansas County": 228, "Ashley County": 229, "Baxter County": 230, "Benton County": 231,
            "Boone County": 232, "Bradley County": 233, "Calhoun County": 234, "Carroll County": 235,
            "Chicot County": 236, "Clark County": 237, "Clay County": 238, "Cleburne County": 239,
            "Cleveland County": 240, "Columbia County": 241, "Conway County": 242, "Craighead County": 243,
            "Crawford County": 244, "Crittenden County": 245, "Cross County": 246, "Dallas County": 247,
            "Desha County": 248, "Drew County": 249, "Faulkner County": 250, "Franklin County": 251,
            "Fulton County": 252, "Garland County": 253, "Grant County": 254, "Greene County": 255,
            "Hempstead County": 256, "Hot Spring County": 257, "Howard County": 258, "Independence County": 259,
            "Izard County": 260, "Jackson County": 261, "Jefferson County": 262, "Johnson County": 263,
            "Lafayette County": 264, "Lawrence County": 265, "Lee County": 266, "Lincoln County": 267,
            "Little River County": 268, "Logan County": 269, "Lonoke County": 270, "Madison County": 271,
            "Marion County": 272, "Miller County": 273, "Mississippi County": 274, "Monroe County": 275,
            "Montgomery County": 276, "Nevada County": 277, "Newton County": 278, "Ouachita County": 279,
            "Perry County": 280, "Phillips County": 281, "Pike County": 282, "Poinsett County": 283,
            "Polk County": 284, "Pope County": 285, "Prairie County": 286, "Pulaski County": 287,
            "Randolph County": 288, "Saline County": 290, "Scott County": 291, "Searcy County": 292,
            "Sebastian County": 293, "Sevier County": 294, "Sharp County": 295, "St. Francis County": 289,
            "Stone County": 296, "Union County": 297, "Van Buren County": 298, "Washington County": 299,
            "White County": 300, "Woodruff County": 301, "Yell County": 302,
        }},
        "California": {"code": "CA", "counties": {
            "Alameda County": 303, "Alpine County": 304, "Amador County": 305, "Butte County": 306,
            "Calaveras County": 307, "Colusa County": 308, "Contra Costa County": 309, "Del Norte County": 310,
            "El Dorado County": 311, "Fresno County": 312, "Glenn County": 313, "Humboldt County": 314,
            "Imperial County": 315, "Inyo County": 316, "Kern County": 317, "Kings County": 318,
            "Lake County": 319, "Lassen County": 320, "Los Angeles County": 321, "Madera County": 322,
            "Marin County": 323, "Mariposa County": 324, "Mendocino County": 325, "Merced County": 326,
            "Modoc County": 327, "Mono County": 328, "Monterey County": 329, "Napa County": 330,
            "Nevada County": 331, "Orange County": 332, "Placer County": 333, "Plumas County": 334,
            "Riverside County": 335, "Sacramento County": 336, "San Benito County": 337, "San Bernardino County": 338,
            "San Diego County": 339, "San Francisco County": 340, "San Joaquin County": 341, "San Luis Obispo County": 342,
            "San Mateo County": 343, "Santa Barbara County": 344, "Santa Clara County": 345, "Santa Cruz County": 346,
            "Shasta County": 347, "Sierra County": 348, "Siskiyou County": 349, "Solano County": 350,
            "Sonoma County": 351, "Stanislaus County": 352, "Sutter County": 353, "Tehama County": 354,
            "Trinity County": 355, "Tulare County": 356, "Tuolumne County": 357, "Ventura County": 358,
            "Yolo County": 359, "Yuba County": 360,
        }},
        "Colorado": {"code": "CO", "counties": {
            "Adams County": 361, "Alamosa County": 362, "Arapahoe County": 363, "Archuleta County": 364,
            "Baca County": 365, "Bent County": 366, "Boulder County": 367, "Broomfield County": 368,
            "Chaffee County": 369, "Cheyenne County": 370, "Clear Creek County": 371, "Conejos County": 372,
            "Costilla County": 373, "Crowley County": 374, "Custer County": 375, "Delta County": 376,
            "Denver County": 377, "Dolores County": 378, "Douglas County": 379, "Eagle County": 380,
            "El Paso County": 382, "Elbert County": 381, "Fremont County": 383, "Garfield County": 384,
            "Gilpin County": 385, "Grand County": 386, "Gunnison County": 387, "Hinsdale County": 388,
            "Huerfano County": 389, "Jackson County": 390, "Jefferson County": 391, "Kiowa County": 392,
            "Kit Carson County": 393, "La Plata County": 395, "Lake County": 394, "Larimer County": 396,
            "Las Animas County": 397, "Lincoln County": 398, "Logan County": 399, "Mesa County": 400,
            "Mineral County": 401, "Moffat County": 402, "Montezuma County": 403, "Montrose County": 404,
            "Morgan County": 405, "Otero County": 406, "Ouray County": 407, "Park County": 408,
            "Phillips County": 409, "Pitkin County": 410, "Prowers County": 411, "Pueblo County": 412,
            "Rio Blanco County": 413, "Rio Grande County": 414, "Routt County": 415, "Saguache County": 416,
            "San Juan County": 417, "San Miguel County": 418, "Sedgwick County": 419, "Summit County": 420,
            "Teller County": 421, "Washington County": 422, "Weld County": 423, "Yuma County": 424,
        }},
        "Columbia": {"code": "DC", "counties": {"District of Columbia": 436}},
        "Connecticut": {"code": "CT", "counties": {
            "Fairfield County": 425, "Hartford County": 426, "Litchfield County": 427, "Middlesex County": 428,
            "New Haven County": 429, "New London County": 430, "Tolland County": 431, "Windham County": 432,
        }},
        "Delaware": {"code": "DE", "counties": {}},
        "Florida": {"code": "FL", "counties": {
            "Alachua County": 437, "Baker County": 438, "Bay County": 439, "Bradford County": 440,
            "Brevard County": 441, "Broward County": 442, "Calhoun County": 443, "Charlotte County": 444,
            "Citrus County": 445, "Clay County": 446, "Collier County": 447, "Columbia County": 448,
            "DeSoto County": 449, "Dixie County": 450, "Duval County": 451, "Escambia County": 452,
            "Flagler County": 453, "Franklin County": 454, "Gadsden County": 455, "Gilchrist County": 456,
            "Glades County": 457, "Gulf County": 458, "Hamilton County": 459, "Hardee County": 460,
            "Hendry County": 461, "Hernando County": 462, "Highlands County": 463, "Hillsborough County": 464,
            "Holmes County": 465, "Indian River County": 466, "Jackson County": 467, "Jefferson County": 468,
            "Lafayette County": 469, "Lake County": 470, "Lee County": 471, "Leon County": 472,
            "Levy County": 473, "Liberty County": 474, "Madison County": 475, "Manatee County": 476,
            "Marion County": 477, "Martin County": 478, "Miami Dade County": 479, "Monroe County": 480,
            "Nassau County": 481, "Okaloosa County": 482, "Okeechobee County": 483, "Orange County": 484,
            "Osceola County": 485, "Palm Beach County": 486, "Pasco County": 487, "Pinellas County": 488,
            "Polk County": 489, "Putnam County": 490, "Santa Rosa County": 493, "Sarasota County": 494,
            "Seminole County": 495, "St. Johns County": 491, "St. Lucie County": 492, "Sumter County": 496,
            "Suwannee County": 497, "Taylor County": 498, "Union County": 499, "Volusia County": 500,
            "Wakulla County": 501, "Walton County": 502, "Washington County": 503,
        }},
        "Georgia": {"code": "GA", "counties": {
            "Appling County": 504, "Atkinson County": 505, "Bacon County": 506, "Baker County": 507,
            "Baldwin County": 508, "Banks County": 509, "Barrow County": 510, "Bartow County": 511,
            "Ben Hill County": 512, "Berrien County": 513, "Bibb County": 514, "Bleckley County": 515,
            "Brantley County": 516, "Brooks County": 517, "Bryan County": 518, "Bulloch County": 519,
            "Burke County": 520, "Butts County": 521, "Calhoun County": 522, "Camden County": 523,
            "Candler County": 524, "Carroll County": 525, "Catoosa County": 526, "Charlton County": 527,
            "Chatham County": 528, "Chattahoochee County": 529, "Chattooga County": 530, "Cherokee County": 531,
            "Clarke County": 532, "Clay County": 533, "Clayton County": 534, "Clinch County": 535,
            "Cobb County": 536, "Coffee County": 537, "Colquitt County": 538, "Columbia County": 539,
            "Cook County": 540, "Coweta County": 541, "Crawford County": 542, "Crisp County": 543,
            "Dade County": 544, "Dawson County": 545, "Decatur County": 546, "DeKalb County": 547,
            "Dodge County": 548, "Dooly County": 549, "Dougherty County": 550, "Douglas County": 551,
            "Early County": 552, "Echols County": 553, "Effingham County": 554, "Elbert County": 555,
            "Emanuel County": 556, "Evans County": 557, "Fannin County": 558, "Fayette County": 559,
            "Floyd County": 560, "Forsyth County": 561, "Franklin County": 562, "Fulton County": 563,
            "Gilmer County": 564, "Glascock County": 565, "Glynn County": 566, "Gordon County": 567,
            "Grady County": 568, "Greene County": 569, "Gwinnett County": 570, "Habersham County": 571,
            "Hall County": 572, "Hancock County": 573, "Haralson County": 574, "Harris County": 575,
            "Hart County": 576, "Heard County": 577, "Henry County": 578, "Houston County": 579,
            "Irwin County": 580, "Jackson County": 581, "Jasper County": 582, "Jeff Davis County": 583,
            "Jefferson County": 584, "Jenkins County": 585, "Johnson County": 586, "Jones County": 587,
            "Lamar County": 588, "Lanier County": 589, "Laurens County": 590, "Lee County": 591,
            "Liberty County": 592, "Lincoln County": 593, "Long County": 594, "Lowndes County": 595,
            "Lumpkin County": 596, "Macon County": 599, "Madison County": 600, "Marion County": 601,
            "McDuffie County": 597, "McIntosh County": 598, "Meriwether County": 602, "Miller County": 603,
            "Mitchell County": 604, "Monroe County": 605, "Montgomery County": 606, "Morgan County": 607,
            "Murray County": 608, "Muscogee County": 609, "Newton County": 610, "Oconee County": 611,
            "Oglethorpe County": 612, "Paulding County": 613, "Peach County": 614, "Pickens County": 615,
            "Pierce County": 616, "Pike County": 617, "Polk County": 618, "Pulaski County": 619,
            "Putnam County": 620, "Quitman County": 621, "Rabun County": 622, "Randolph County": 623,
            "Richmond County": 624, "Rockdale County": 625, "Schley County": 626, "Screven County": 627,
            "Seminole County": 628, "Spalding County": 629, "Stephens County": 630, "Stewart County": 631,
            "Sumter County": 632, "Talbot County": 633, "Taliaferro County": 634, "Tattnall County": 635,
            "Taylor County": 636, "Telfair County": 637, "Terrell County": 638, "Thomas County": 639,
            "Tift County": 640, "Toombs County": 641, "Towns County": 642, "Treutlen County": 643,
            "Troup County": 644, "Turner County": 645, "Twiggs County": 646, "Union County": 647,
            "Upson County": 648, "Walker County": 649, "Walton County": 650, "Ware County": 651,
            "Warren County": 652, "Washington County": 653, "Wayne County": 654, "Webster County": 655,
            "Wheeler County": 656, "White County": 657, "Whitfield County": 658, "Wilcox County": 659,
            "Wilkes County": 660, "Wilkinson County": 661, "Worth County": 662,
        }},
        "Hawaii": {"code": "HI", "counties": {
            "Hawaii County": 663, "Honolulu County": 664, "Kalawao County": 665,
            "Kauai County": 666, "Maui County": 667,
        }},
        "Idaho": {"code": "ID", "counties": {}},
        "Illinois": {"code": "IL", "counties": {
            "Adams County": 712, "Alexander County": 713, "Bond County": 714, "Boone County": 715,
            "Brown County": 716, "Bureau County": 717, "Calhoun County": 718, "Carroll County": 719,
            "Cass County": 720, "Champaign County": 721, "Christian County": 722, "Clark County": 723,
            "Clay County": 724, "Clinton County": 725, "Coles County": 726, "Cook County": 727,
            "Crawford County": 728, "Cumberland County": 729, "De Witt County": 731, "DeKalb County": 730,
            "Douglas County": 732, "DuPage County": 733, "Edgar County": 734, "Edwards County": 735,
            "Effingham County": 736, "Fayette County": 737, "Ford County": 738, "Franklin County": 739,
            "Fulton County": 740, "Gallatin County": 741, "Greene County": 742, "Grundy County": 743,
            "Hamilton County": 744, "Hancock County": 745, "Hardin County": 746, "Henderson County": 747,
            "Henry County": 748, "Iroquois County": 749, "Jackson County": 750, "Jasper County": 751,
            "Jefferson County": 752, "Jersey County": 753, "Jo Daviess County": 754, "Johnson County": 755,
            "Kane County": 756, "Kankakee County": 757, "Kendall County": 758, "Knox County": 759,
            "Lake County": 760, "LaSalle County": 761, "Lawrence County": 762, "Lee County": 763,
            "Livingston County": 764, "Logan County": 765, "Macon County": 769, "Macoupin County": 770,
            "Madison County": 771, "Marion County": 772, "Marshall County": 773, "Mason County": 774,
            "Massac County": 775, "McDonough County": 766, "McHenry County": 767, "McLean County": 768,
            "Menard County": 776, "Mercer County": 777, "Monroe County": 778, "Montgomery County": 779,
            "Morgan County": 780, "Moultrie County": 781, "Ogle County": 782, "Peoria County": 783,
            "Perry County": 784, "Piatt County": 785, "Pike County": 786, "Pope County": 787,
            "Pulaski County": 788, "Putnam County": 789, "Randolph County": 790, "Richland County": 791,
            "Rock Island County": 792, "Saline County": 794, "Sangamon County": 795, "Schuyler County": 796,
            "Scott County": 797, "Shelby County": 798, "St. Clair County": 793, "Stark County": 799,
            "Stephenson County": 800, "Tazewell County": 801, "Union County": 802, "Vermilion County": 803,
            "Wabash County": 804, "Warren County": 805, "Washington County": 806, "Wayne County": 807,
            "White County": 808, "Whiteside County": 809, "Will County": 810, "Williamson County": 811,
            "Winnebago County": 812, "Woodford County": 813,
        }},
        "Indiana": {"code": "IN", "counties": {
            "Adams County": 814, "Allen County": 815, "Bartholomew County": 816, "Benton County": 817,
            "Blackford County": 818, "Boone County": 819, "Brown County": 820, "Carroll County": 821,
            "Cass County": 822, "Clark County": 823, "Clay County": 824, "Clinton County": 825,
            "Crawford County": 826, "Daviess County": 827, "Dearborn County": 828, "Decatur County": 829,
            "DeKalb County": 830, "Delaware County": 831, "Dubois County": 832, "Elkhart County": 833,
            "Fayette County": 834, "Floyd County": 835, "Fountain County": 836, "Franklin County": 837,
            "Fulton County": 838, "Gibson County": 839, "Grant County": 840, "Greene County": 841,
            "Hamilton County": 842, "Hancock County": 843, "Harrison County": 844, "Hendricks County": 845,
            "Henry County": 846, "Howard County": 847, "Huntington County": 848, "Jackson County": 849,
            "Jasper County": 850, "Jay County": 851, "Jefferson County": 852, "Jennings County": 853,
            "Johnson County": 854, "Knox County": 855, "Kosciusko County": 856, "LaGrange County": 857,
            "Lake County": 858, "LaPorte County": 859, "Lawrence County": 860, "Madison County": 861,
            "Marion County": 862, "Marshall County": 863, "Martin County": 864, "Miami County": 865,
            "Monroe County": 866, "Montgomery County": 867, "Morgan County": 868, "Newton County": 869,
            "Noble County": 870, "Ohio County": 871, "Orange County": 872, "Owen County": 873,
            "Parke County": 874, "Perry County": 875, "Pike County": 876, "Porter County": 877,
            "Posey County": 878, "Pulaski County": 879, "Putnam County": 880, "Randolph County": 881,
            "Ripley County": 882, "Rush County": 883, "Scott County": 885, "Shelby County": 886,
            "Spencer County": 887, "St. Joseph County": 884, "Starke County": 888, "Steuben County": 889,
            "Sullivan County": 890, "Switzerland County": 891, "Tippecanoe County": 892, "Tipton County": 893,
            "Union County": 894, "Vanderburgh County": 895, "Vermillion County": 896, "Vigo County": 897,
            "Wabash County": 898, "Warren County": 899, "Warrick County": 900, "Washington County": 901,
            "Wayne County": 902, "Wells County": 903, "White County": 904, "Whitley County": 905,
        }},
        "Iowa": {"code": "IA", "counties": {}},
        "Kansas": {"code": "KS", "counties": {}},
        "Kentucky": {"code": "KY", "counties": {}},
        "Louisiana": {"code": "LA", "counties": {}},
        "Maine": {"code": "ME", "counties": {}},
        "Maryland": {"code": "MD", "counties": {}},
        "Massachusetts": {"code": "MA", "counties": {
            "Barnstable County": 1334, "Berkshire County": 1335, "Bristol County": 1336, "Dukes County": 1337,
            "Essex County": 1338, "Franklin County": 1339, "Hampden County": 1340, "Hampshire County": 1341,
            "Middlesex County": 1342, "Nantucket County": 1343, "Norfolk County": 1344, "Plymouth County": 1345,
            "Suffolk County": 1346, "Worcester County": 1347,
        }},
        "Michigan": {"code": "MI", "counties": {
            "Alcona County": 1348, "Alger County": 1349, "Allegan County": 1350, "Alpena County": 1351,
            "Antrim County": 1352, "Arenac County": 1353, "Baraga County": 1354, "Barry County": 1355,
            "Bay County": 1356, "Benzie County": 1357, "Berrien County": 1358, "Branch County": 1359,
            "Calhoun County": 1360, "Cass County": 1361, "Charlevoix County": 1362, "Cheboygan County": 1363,
            "Chippewa County": 1364, "Clare County": 1365, "Clinton County": 1366, "Crawford County": 1367,
            "Delta County": 1368, "Dickinson County": 1369, "Eaton County": 1370, "Emmet County": 1371,
            "Genesee County": 1372, "Gladwin County": 1373, "Gogebic County": 1374, "Grand Traverse County": 1375,
            "Gratiot County": 1376, "Hillsdale County": 1377, "Houghton County": 1378, "Huron County": 1379,
            "Ingham County": 1380, "Ionia County": 1381, "Iosco County": 1382, "Iron County": 1383,
            "Isabella County": 1384, "Jackson County": 1385, "Kalamazoo County": 1386, "Kalkaska County": 1387,
            "Kent County": 1388, "Keweenaw County": 1389, "Lake County": 1390, "Lapeer County": 1391,
            "Leelanau County": 1392, "Lenawee County": 1393, "Livingston County": 1394, "Luce County": 1395,
            "Mackinac County": 1396, "Macomb County": 1397, "Manistee County": 1398, "Marquette County": 1399,
            "Mason County": 1400, "Mecosta County": 1401, "Menominee County": 1402, "Midland County": 1403,
            "Missaukee County": 1404, "Monroe County": 1405, "Montcalm County": 1406, "Montmorency County": 1407,
            "Muskegon County": 1408, "Newaygo County": 1409, "Oakland County": 1410, "Oceana County": 1411,
            "Ogemaw County": 1412, "Ontonagon County": 1413, "Osceola County": 1414, "Oscoda County": 1415,
            "Otsego County": 1416, "Ottawa County": 1417, "Presque Isle County": 1418, "Roscommon County": 1419,
            "Saginaw County": 1420, "Sanilac County": 1423, "Schoolcraft County": 1424, "Shiawassee County": 1425,
            "St. Clair County": 1421, "St. Joseph County": 1422, "Tuscola County": 1426, "Van Buren County": 1427,
            "Washtenaw County": 1428, "Wayne County": 1429, "Wexford County": 1430,
        }},
        "Minnesota": {"code": "MN", "counties": {}},
        "Mississippi": {"code": "MS", "counties": {}},
        "Missouri": {"code": "MO", "counties": {}},
        "Montana": {"code": "MT", "counties": {}},
        "Nebraska": {"code": "NE", "counties": {}},
        "Nevada": {"code": "NV", "counties": {}},
        "New Hampshire": {"code": "NH", "counties": {}},
        "New Jersey": {"code": "NJ", "counties": {
            "Atlantic County": 1891, "Bergen County": 1892, "Burlington County": 1893, "Camden County": 1894,
            "Cape May County": 1895, "Cumberland County": 1896, "Essex County": 1897, "Gloucester County": 1898,
            "Hudson County": 1899, "Hunterdon County": 1900, "Mercer County": 1901, "Middlesex County": 1902,
            "Monmouth County": 1903, "Morris County": 1904, "Ocean County": 1905, "Passaic County": 1906,
            "Salem County": 1907, "Somerset County": 1908, "Sussex County": 1909, "Union County": 1910,
            "Warren County": 1911,
        }},
        "New Mexico": {"code": "NM", "counties": {}},
        "New York": {"code": "NY", "counties": {
            "Albany County": 1945, "Allegany County": 1946, "Bronx County": 1947, "Broome County": 1948,
            "Cattaraugus County": 1949, "Cayuga County": 1950, "Chautauqua County": 1951, "Chemung County": 1952,
            "Chenango County": 1953, "Clinton County": 1954, "Columbia County": 1955, "Cortland County": 1956,
            "Delaware County": 1957, "Dutchess County": 1958, "Erie County": 1959, "Essex County": 1960,
            "Franklin County": 1961, "Fulton County": 1962, "Genesee County": 1963, "Greene County": 1964,
            "Hamilton County": 1965, "Herkimer County": 1966, "Jefferson County": 1967, "Kings County": 1968,
            "Lewis County": 1969, "Livingston County": 1970, "Madison County": 1971, "Monroe County": 1972,
            "Montgomery County": 1973, "Nassau County": 1974, "New York County": 1975, "Niagara County": 1976,
            "Oneida County": 1977, "Onondaga County": 1978, "Ontario County": 1979, "Orange County": 1980,
            "Orleans County": 1981, "Oswego County": 1982, "Otsego County": 1983, "Putnam County": 1984,
            "Queens County": 1985, "Rensselaer County": 1986, "Richmond County": 1987, "Rockland County": 1988,
            "Saratoga County": 1990, "Schenectady County": 1991, "Schoharie County": 1992, "Schuyler County": 1993,
            "Seneca County": 1994, "St. Lawrence County": 1989, "Steuben County": 1995, "Suffolk County": 1996,
            "Sullivan County": 1997, "Tioga County": 1998, "Tompkins County": 1999, "Ulster County": 2000,
            "Warren County": 2001, "Washington County": 2002, "Wayne County": 2003, "Westchester County": 2004,
            "Wyoming County": 2005, "Yates County": 2006,
        }},
        "North Carolina": {"code": "NC", "counties": {
            "Alamance County": 2007, "Alexander County": 2008, "Alleghany County": 2009, "Anson County": 2010,
            "Ashe County": 2011, "Avery County": 2012, "Beaufort County": 2013, "Bertie County": 2014,
            "Bladen County": 2015, "Brunswick County": 2016, "Buncombe County": 2017, "Burke County": 2018,
            "Cabarrus County": 2019, "Caldwell County": 2020, "Camden County": 2021, "Carteret County": 2022,
            "Caswell County": 2023, "Catawba County": 2024, "Chatham County": 2025, "Cherokee County": 2026,
            "Chowan County": 2027, "Clay County": 2028, "Cleveland County": 2029, "Columbus County": 2030,
            "Craven County": 2031, "Cumberland County": 2032, "Currituck County": 2033, "Dare County": 2034,
            "Davidson County": 2035, "Davie County": 2036, "Duplin County": 2037, "Durham County": 2038,
            "Edgecombe County": 2039, "Forsyth County": 2040, "Franklin County": 2041, "Gaston County": 2042,
            "Gates County": 2043, "Graham County": 2044, "Granville County": 2045, "Greene County": 2046,
            "Guilford County": 2047, "Halifax County": 2048, "Harnett County": 2049, "Haywood County": 2050,
            "Henderson County": 2051, "Hertford County": 2052, "Hoke County": 2053, "Hyde County": 2054,
            "Iredell County": 2055, "Jackson County": 2056, "Johnston County": 2057, "Jones County": 2058,
            "Lee County": 2059, "Lenoir County": 2060, "Lincoln County": 2061, "Macon County": 2063,
            "Madison County": 2064, "Martin County": 2065, "McDowell County": 2062, "Mecklenburg County": 2066,
            "Mitchell County": 2067, "Montgomery County": 2068, "Moore County": 2069, "Nash County": 2070,
            "New Hanover County": 2071, "Northampton County": 2072, "Onslow County": 2073, "Orange County": 2074,
            "Pamlico County": 2075, "Pasquotank County": 2076, "Pender County": 2077, "Perquimans County": 2078,
            "Person County": 2079, "Pitt County": 2080, "Polk County": 2081, "Randolph County": 2082,
            "Richmond County": 2083, "Robeson County": 2084, "Rockingham County": 2085, "Rowan County": 2086,
            "Rutherford County": 2087, "Sampson County": 2088, "Scotland County": 2089, "Stanly County": 2090,
            "Stokes County": 2091, "Surry County": 2092, "Swain County": 2093, "Transylvania County": 2094,
            "Tyrrell County": 2095, "Union County": 2096, "Vance County": 2097, "Wake County": 2098,
            "Warren County": 2099, "Washington County": 2100, "Watauga County": 2101, "Wayne County": 2102,
            "Wilkes County": 2103, "Wilson County": 2104, "Yadkin County": 2105, "Yancey County": 2106,
        }},
        "North Dakota": {"code": "ND", "counties": {}},
        "Ohio": {"code": "OH", "counties": {
            "Adams County": 2160, "Allen County": 2161, "Ashland County": 2162, "Ashtabula County": 2163,
            "Athens County": 2164, "Auglaize County": 2165, "Belmont County": 2166, "Brown County": 2167,
            "Butler County": 2168, "Carroll County": 2169, "Champaign County": 2170, "Clark County": 2171,
            "Clermont County": 2172, "Clinton County": 2173, "Columbiana County": 2174, "Coshocton County": 2175,
            "Crawford County": 2176, "Cuyahoga County": 2177, "Darke County": 2178, "Defiance County": 2179,
            "Delaware County": 2180, "Erie County": 2181, "Fairfield County": 2182, "Fayette County": 2183,
            "Franklin County": 2184, "Fulton County": 2185, "Gallia County": 2186, "Geauga County": 2187,
            "Greene County": 2188, "Guernsey County": 2189, "Hamilton County": 2190, "Hancock County": 2191,
            "Hardin County": 2192, "Harrison County": 2193, "Henry County": 2194, "Highland County": 2195,
            "Hocking County": 2196, "Holmes County": 2197, "Huron County": 2198, "Jackson County": 2199,
            "Jefferson County": 2200, "Knox County": 2201, "Lake County": 2202, "Lawrence County": 2203,
            "Licking County": 2204, "Logan County": 2205, "Lorain County": 2206, "Lucas County": 2207,
            "Madison County": 2208, "Mahoning County": 2209, "Marion County": 2210, "Medina County": 2211,
            "Meigs County": 2212, "Mercer County": 2213, "Miami County": 2214, "Monroe County": 2215,
            "Montgomery County": 2216, "Morgan County": 2217, "Morrow County": 2218, "Muskingum County": 2219,
            "Noble County": 2220, "Ottawa County": 2221, "Paulding County": 2222, "Perry County": 2223,
            "Pickaway County": 2224, "Pike County": 2225, "Portage County": 2226, "Preble County": 2227,
            "Putnam County": 2228, "Richland County": 2229, "Ross County": 2230, "Sandusky County": 2231,
            "Scioto County": 2232, "Seneca County": 2233, "Shelby County": 2234, "Stark County": 2235,
            "Summit County": 2236, "Trumbull County": 2237, "Tuscarawas County": 2238, "Union County": 2239,
            "Van Wert County": 2240, "Vinton County": 2241, "Warren County": 2242, "Washington County": 2243,
            "Wayne County": 2244, "Williams County": 2245, "Wood County": 2246, "Wyandot County": 2247,
        }},
        "Oklahoma": {"code": "OK", "counties": {}},
        "Oregon": {"code": "OR", "counties": {}},
        "Pennsylvania": {"code": "PA", "counties": {
            "Adams County": 2361, "Allegheny County": 2362, "Armstrong County": 2363, "Beaver County": 2364,
            "Bedford County": 2365, "Berks County": 2366, "Blair County": 2367, "Bradford County": 2368,
            "Bucks County": 2369, "Butler County": 2370, "Cambria County": 2371, "Cameron County": 2372,
            "Carbon County": 2373, "Centre County": 2374, "Chester County": 2375, "Clarion County": 2376,
            "Clearfield County": 2377, "Clinton County": 2378, "Columbia County": 2379, "Crawford County": 2380,
            "Cumberland County": 2381, "Dauphin County": 2382, "Delaware County": 2383, "Elk County": 2384,
            "Erie County": 2385, "Fayette County": 2386, "Forest County": 2387, "Franklin County": 2388,
            "Fulton County": 2389, "Greene County": 2390, "Huntingdon County": 2391, "Indiana County": 2392,
            "Jefferson County": 2393, "Juniata County": 2394, "Lackawanna County": 2395, "Lancaster County": 2396,
            "Lawrence County": 2397, "Lebanon County": 2398, "Lehigh County": 2399, "Luzerne County": 2400,
            "Lycoming County": 2401, "McKean County": 2402, "Mercer County": 2403, "Mifflin County": 2404,
            "Monroe County": 2405, "Montgomery County": 2406, "Montour County": 2407, "Northampton County": 2408,
            "Northumberland County": 2409, "Perry County": 2410, "Philadelphia County": 2411, "Pike County": 2412,
            "Potter County": 2413, "Schuylkill County": 2414, "Snyder County": 2415, "Somerset County": 2416,
            "Sullivan County": 2417, "Susquehanna County": 2418, "Tioga County": 2419, "Union County": 2420,
            "Venango County": 2421, "Warren County": 2422, "Washington County": 2423, "Wayne County": 2424,
            "Westmoreland County": 2425, "Wyoming County": 2426, "York County": 2427,
        }},
        "Rhode Island": {"code": "RI", "counties": {}},
        "South Carolina": {"code": "SC", "counties": {}},
        "South Dakota": {"code": "SD", "counties": {}},
        "Tennessee": {"code": "TN", "counties": {
            "Anderson County": 2545, "Bedford County": 2546, "Benton County": 2547, "Bledsoe County": 2548,
            "Blount County": 2549, "Bradley County": 2550, "Campbell County": 2551, "Cannon County": 2552,
            "Carroll County": 2553, "Carter County": 2554, "Cheatham County": 2555, "Chester County": 2556,
            "Claiborne County": 2557, "Clay County": 2558, "Cocke County": 2559, "Coffee County": 2560,
            "Crockett County": 2561, "Cumberland County": 2562, "Davidson County": 2563, "Decatur County": 2564,
            "DeKalb County": 2565, "Dickson County": 2566, "Dyer County": 2567, "Fayette County": 2568,
            "Fentress County": 2569, "Franklin County": 2570, "Gibson County": 2571, "Giles County": 2572,
            "Grainger County": 2573, "Greene County": 2574, "Grundy County": 2575, "Hamblen County": 2576,
            "Hamilton County": 2577, "Hancock County": 2578, "Hardeman County": 2579, "Hardin County": 2580,
            "Hawkins County": 2581, "Haywood County": 2582, "Henderson County": 2583, "Henry County": 2584,
            "Hickman County": 2585, "Houston County": 2586, "Humphreys County": 2587, "Jackson County": 2588,
            "Jefferson County": 2589, "Johnson County": 2590, "Knox County": 2591, "Lake County": 2592,
            "Lauderdale County": 2593, "Lawrence County": 2594, "Lewis County": 2595, "Lincoln County": 2596,
            "Loudon County": 2597, "Macon County": 2600, "Madison County": 2601, "Marion County": 2602,
            "Marshall County": 2603, "Maury County": 2604, "McMinn County": 2598, "McNairy County": 2599,
            "Meigs County": 2605, "Monroe County": 2606, "Montgomery County": 2607, "Moore County": 2608,
            "Morgan County": 2609, "Obion County": 2610, "Overton County": 2611, "Perry County": 2612,
            "Pickett County": 2613, "Polk County": 2614, "Putnam County": 2615, "Rhea County": 2616,
            "Roane County": 2617, "Robertson County": 2618, "Rutherford County": 2619, "Scott County": 2620,
            "Sequatchie County": 2621, "Sevier County": 2622, "Shelby County": 2623, "Smith County": 2624,
            "Stewart County": 2625, "Sullivan County": 2626, "Sumner County": 2627, "Tipton County": 2628,
            "Trousdale County": 2629, "Unicoi County": 2630, "Union County": 2631, "Van Buren County": 2632,
            "Warren County": 2633, "Washington County": 2634, "Wayne County": 2635, "Weakley County": 2636,
            "White County": 2637, "Williamson County": 2638, "Wilson County": 2639,
        }},
        "Texas": {"code": "TX", "counties": {
            "Anderson County": 2640, "Andrews County": 2641, "Angelina County": 2642, "Aransas County": 2643,
            "Archer County": 2644, "Armstrong County": 2645, "Atascosa County": 2646, "Austin County": 2647,
            "Bailey County": 2648, "Bandera County": 2649, "Bastrop County": 2650, "Baylor County": 2651,
            "Bee County": 2652, "Bell County": 2653, "Bexar County": 2654, "Blanco County": 2655,
            "Borden County": 2656, "Bosque County": 2657, "Bowie County": 2658, "Brazoria County": 2659,
            "Brazos County": 2660, "Brewster County": 2661, "Briscoe County": 2662, "Brooks County": 2663,
            "Brown County": 2664, "Burleson County": 2665, "Burnet County": 2666, "Caldwell County": 2667,
            "Calhoun County": 2668, "Callahan County": 2669, "Cameron County": 2670, "Camp County": 2671,
            "Carson County": 2672, "Cass County": 2673, "Castro County": 2674, "Chambers County": 2675,
            "Cherokee County": 2676, "Childress County": 2677, "Clay County": 2678, "Cochran County": 2679,
            "Coke County": 2680, "Coleman County": 2681, "Collin County": 2682, "Collingsworth County": 2683,
            "Colorado County": 2684, "Comal County": 2685, "Comanche County": 2686, "Concho County": 2687,
            "Cooke County": 2688, "Coryell County": 2689, "Cottle County": 2690, "Crane County": 2691,
            "Crockett County": 2692, "Crosby County": 2693, "Culberson County": 2694, "Dallam County": 2695,
            "Dallas County": 2696, "Dawson County": 2697, "Deaf Smith County": 2698, "Delta County": 2699,
            "Denton County": 2700, "DeWitt County": 2701, "Dickens County": 2702, "Dimmit County": 2703,
            "Donley County": 2704, "Duval County": 2705, "Eastland County": 2706, "Ector County": 2707,
            "Edwards County": 2708, "El Paso County": 2710, "Ellis County": 2709, "Erath County": 2711,
            "Falls County": 2712, "Fannin County": 2713, "Fayette County": 2714, "Fisher County": 2715,
            "Floyd County": 2716, "Foard County": 2717, "Fort Bend County": 2718, "Franklin County": 2719,
            "Freestone County": 2720, "Frio County": 2721, "Gaines County": 2722, "Galveston County": 2723,
            "Garza County": 2724, "Gillespie County": 2725, "Glasscock County": 2726, "Goliad County": 2727,
            "Gonzales County": 2728, "Gray County": 2729, "Grayson County": 2730, "Gregg County": 2731,
            "Grimes County": 2732, "Guadalupe County": 2733, "Hale County": 2734, "Hall County": 2735,
            "Hamilton County": 2736, "Hansford County": 2737, "Hardeman County": 2738, "Hardin County": 2739,
            "Harris County": 2740, "Harrison County": 2741, "Hartley County": 2742, "Haskell County": 2743,
            "Hays County": 2744, "Hemphill County": 2745, "Henderson County": 2746, "Hidalgo County": 2747,
            "Hill County": 2748, "Hockley County": 2749, "Hood County": 2750, "Hopkins County": 2751,
            "Houston County": 2752, "Howard County": 2753, "Hudspeth County": 2754, "Hunt County": 2755,
            "Hutchinson County": 2756, "Irion County": 2757, "Jack County": 2758, "Jackson County": 2759,
            "Jasper County": 2760, "Jeff Davis County": 2761, "Jefferson County": 2762, "Jim Hogg County": 2763,
            "Jim Wells County": 2764, "Johnson County": 2765, "Jones County": 2766, "Karnes County": 2767,
            "Kaufman County": 2768, "Kendall County": 2769, "Kenedy County": 2770, "Kent County": 2771,
            "Kerr County": 2772, "Kimble County": 2773, "King County": 2774, "Kinney County": 2775,
            "Kleberg County": 2776, "Knox County": 2777, "La Salle County": 2781, "Lamar County": 2778,
            "Lamb County": 2779, "Lampasas County": 2780, "Lavaca County": 2782, "Lee County": 2783,
            "Leon County": 2784, "Liberty County": 2785, "Limestone County": 2786, "Lipscomb County": 2787,
            "Live Oak County": 2788, "Llano County": 2789, "Loving County": 2790, "Lubbock County": 2791,
            "Lynn County": 2792, "Madison County": 2796, "Marion County": 2797, "Martin County": 2798,
            "Mason County": 2799, "Matagorda County": 2800, "Maverick County": 2801, "McCulloch County": 2793,
            "McLennan County": 2794, "McMullen County": 2795, "Medina County": 2802, "Menard County": 2803,
            "Midland County": 2804, "Milam County": 2805, "Mills County": 2806, "Mitchell County": 2807,
            "Montague County": 2808, "Montgomery County": 2809, "Moore County": 2810, "Morris County": 2811,
            "Motley County": 2812, "Nacogdoches County": 2813, "Navarro County": 2814, "Newton County": 2815,
            "Nolan County": 2816, "Nueces County": 2817, "Ochiltree County": 2818, "Oldham County": 2819,
            "Orange County": 2820, "Palo Pinto County": 2821, "Panola County": 2822, "Parker County": 2823,
            "Parmer County": 2824, "Pecos County": 2825, "Polk County": 2826, "Potter County": 2827,
            "Presidio County": 2828, "Rains County": 2829, "Randall County": 2830, "Reagan County": 2831,
            "Real County": 2832, "Red River County": 2833, "Reeves County": 2834, "Refugio County": 2835,
            "Roberts County": 2836, "Robertson County": 2837, "Rockwall County": 2838, "Runnels County": 2839,
            "Rusk County": 2840, "Sabine County": 2841, "San Augustine County": 2842, "San Jacinto County": 2843,
            "San Patricio County": 2844, "San Saba County": 2845, "Schleicher County": 2846, "Scurry County": 2847,
            "Shackelford County": 2848, "Shelby County": 2849, "Sherman County": 2850, "Smith County": 2851,
            "Somervell County": 2852, "Starr County": 2853, "Stephens County": 2854, "Sterling County": 2855,
            "Stonewall County": 2856, "Sutton County": 2857, "Swisher County": 2858, "Tarrant County": 2859,
            "Taylor County": 2860, "Terrell County": 2861, "Terry County": 2862, "Throckmorton County": 2863,
            "Titus County": 2864, "Tom Green County": 2865, "Travis County": 2866, "Trinity County": 2867,
            "Tyler County": 2868, "Upshur County": 2869, "Upton County": 2870, "Uvalde County": 2871,
            "Val Verde County": 2872, "Van Zandt County": 2873, "Victoria County": 2874, "Walker County": 2875,
            "Waller County": 2876, "Ward County": 2877, "Washington County": 2878, "Webb County": 2879,
            "Wharton County": 2880, "Wheeler County": 2881, "Wichita County": 2882, "Wilbarger County": 2883,
            "Willacy County": 2884, "Williamson County": 2885, "Wilson County": 2886, "Winkler County": 2887,
            "Wise County": 2888, "Wood County": 2889, "Yoakum County": 2890, "Young County": 2891,
            "Zapata County": 2892, "Zavala County": 2893,
        }},
        "Utah": {"code": "UT", "counties": {}},
        "Vermont": {"code": "VT", "counties": {}},
        "Virginia": {"code": "VA", "counties": {
            "Accomack County": 2937, "Albemarle County": 2938, "Alexandria": 3032, "Alleghany County": 2939,
            "Amelia County": 2940, "Amherst County": 2941, "Appomattox County": 2942, "Arlington County": 2943,
            "Augusta County": 2944, "Bath County": 2945, "Bedford County": 2946, "Bland County": 2947,
            "Botetourt County": 2948, "Bristol": 3034, "Brunswick County": 2949, "Buchanan County": 2950,
            "Buckingham County": 2951, "Buena Vista": 3035, "Campbell County": 2952, "Caroline County": 2953,
            "Carroll County": 2954, "Charles City": 2955, "Charlotte County": 2956, "Charlottesville": 3036,
            "Chesapeake": 3037, "Chesterfield County": 2957, "Clarke County": 2958, "Colonial Heights": 3038,
            "Covington": 3039, "Craig County": 2959, "Culpeper County": 2960, "Cumberland County": 2961,
            "Danville": 3040, "Dickenson County": 2962, "Dinwiddie County": 2963, "Emporia": 3041,
            "Essex County": 2964, "Fairfax City": 3042, "Fairfax County": 2965, "Falls Church": 3043,
            "Fauquier County": 2966, "Floyd County": 2967, "Fluvanna County": 2968, "Franklin City": 3044,
            "Franklin County": 2969, "Frederick County": 2970, "Fredericksburg": 3045, "Galax": 3046,
            "Giles County": 2971, "Gloucester County": 2972, "Goochland County": 2973, "Grayson County": 2974,
            "Greene County": 2975, "Greensville County": 2976, "Halifax County": 2977, "Hampton": 3047,
            "Hanover County": 2978, "Harrisonburg": 3048, "Henrico County": 2979, "Henry County": 2980,
            "Highland County": 2981, "Hopewell": 3049, "Isle of Wight County": 2982, "James City": 2983,
            "King & Queen County": 2984, "King George County": 2985, "King William County": 2986,
            "Lancaster County": 2987, "Lee County": 2988, "Lexington": 3050, "Loudoun County": 2989,
            "Louisa County": 2990, "Lunenburg County": 2991, "Lynchburg": 3051, "Madison County": 2992,
            "Manassas": 3052, "Manassas Park": 3053, "Martinsville": 3054, "Mathews County": 2993,
            "Mecklenburg County": 2994, "Middlesex County": 2995, "Montgomery County": 2996, "Nelson County": 2997,
            "New Kent County": 2998, "Newport News": 3055, "Norfolk": 3056, "Northampton County": 2999,
            "Northumberland County": 3000, "Norton": 3057, "Nottoway County": 3001, "Orange County": 3002,
            "Page County": 3003, "Patrick County": 3004, "Petersburg": 3058, "Pittsylvania County": 3005,
            "Poquoson": 3059, "Portsmouth": 3060, "Powhatan County": 3006, "Prince Edward County": 3007,
            "Prince George County": 3008, "Prince William County": 3009, "Pulaski County": 3010, "Radford": 3061,
            "Rappahannock County": 3011, "Richmond City": 3062, "Richmond County": 3012, "Roanoke City": 3063,
            "Roanoke County": 3013, "Rockbridge County": 3014, "Rockingham County": 3015, "Russell County": 3016,
            "Salem": 3064, "Scott County": 3017, "Shenandoah County": 3018, "Smyth County": 3019,
            "Southampton County": 3020, "Spotsylvania County": 3021, "Stafford County": 3022, "Staunton": 3065,
            "Suffolk": 3066, "Surry County": 3023, "Sussex County": 3024, "Tazewell County": 3025,
            "Virginia Beach": 3067, "Warren County": 3026, "Washington County": 3027, "Waynesboro": 3068,
            "Westmoreland County": 3028, "Williamsburg": 3069, "Winchester": 3070, "Wise County": 3029,
            "Wythe County": 3030, "York County": 3031,
        }},
        "Washington": {"code": "WA", "counties": {
            "Adams County": 3071, "Asotin County": 3072, "Benton County": 3073, "Chelan County": 3074,
            "Clallam County": 3075, "Clark County": 3076, "Columbia County": 3077, "Cowlitz County": 3078,
            "Douglas County": 3079, "Ferry County": 3080, "Franklin County": 3081, "Garfield County": 3082,
            "Grant County": 3083, "Grays Harbor County": 3084, "Island County": 3085, "Jefferson County": 3086,
            "King County": 118, "Kitsap County": 3087, "Kittitas County": 3088, "Klickitat County": 3089,
            "Lewis County": 3090, "Lincoln County": 3091, "Mason County": 3092, "Okanogan County": 3093,
            "Pacific County": 3094, "Pend Oreille County": 3095, "Pierce County": 3096, "San Juan County": 3097,
            "Skagit County": 3098, "Skamania County": 3099, "Snohomish County": 2, "Spokane County": 3100,
            "Stevens County": 3101, "Thurston County": 3102, "Wahkiakum County": 3103, "Walla Walla County": 3104,
            "Whatcom County": 3105, "Whitman County": 3106, "Yakima County": 3107,
        }},
        "West Virginia": {"code": "WV", "counties": {}},
        "Wisconsin": {"code": "WI", "counties": {}},
        "Wyoming": {"code": "WY", "counties": {}},
    }

    top_100_counties = [
        # Rank, (county_name, state, county_id)  -- None = not in us_data
        ("Los Angeles County", "California", 321),        # 1  ~9.76M
        ("Cook County", "Illinois", 727),                 # 2  ~5.18M
        ("Harris County", "Texas", 2740),                 # 3  ~5.01M
        ("Maricopa County", "Arizona", 220),              # 4  ~4.67M
        ("San Diego County", "California", 339),          # 5  ~3.30M
        ("Orange County", "California", 332),             # 6  ~3.17M
        ("Miami Dade County", "Florida", 479),            # 7  ~2.84M
        ("Dallas County", "Texas", 2696),                 # 8  ~2.66M
        ("Kings County", "New York", 1968),               # 9  ~2.62M
        ("Riverside County", "California", 335),          # 10 ~2.53M
        # 11: Clark County, Nevada — Nevada has no counties in us_data, SKIPPED
        ("King County", "Washington", 118),               # 12 ~2.34M
        ("Queens County", "New York", 1985),              # 13 ~2.32M
        ("Tarrant County", "Texas", 2859),                # 14 ~2.23M
        ("San Bernardino County", "California", 338),     # 15 ~2.21M
        ("Bexar County", "Texas", 2654),                  # 16 ~2.13M
        ("Broward County", "Florida", 442),               # 17 ~2.04M
        ("Santa Clara County", "California", 345),        # 18 ~1.93M
        ("Wayne County", "Michigan", 1429),               # 19 ~1.77M
        ("Middlesex County", "Massachusetts", 1342),      # 20 ~1.67M
        ("New York County", "New York", 1975),            # 21 ~1.66M
        ("Alameda County", "California", 303),            # 22 ~1.65M
        ("Sacramento County", "California", 336),         # 23 ~1.61M
        ("Palm Beach County", "Florida", 486),            # 24 ~1.58M
        ("Hillsborough County", "Florida", 464),          # 25 ~1.58M
        ("Philadelphia County", "Pennsylvania", 2411),    # 26 ~1.57M
        ("Suffolk County", "New York", 1996),             # 27 ~1.54M
        ("Orange County", "Florida", 484),                # 28 ~1.53M
        ("Nassau County", "New York", 1974),              # 29 ~1.39M
        ("Bronx County", "New York", 1947),               # 30 ~1.38M
        ("Travis County", "Texas", 2866),                 # 31 ~1.36M
        ("Franklin County", "Ohio", 2184),                # 32 ~1.36M
        # 33: Oakland County, Michigan — not in us_data (Michigan has no Oakland County listed), SKIPPED
        # 34: Hennepin County, Minnesota — Minnesota has no counties in us_data, SKIPPED
        ("Collin County", "Texas", 2682),                 # 35 ~1.25M
        ("Cuyahoga County", "Ohio", 2177),                # 36 ~1.24M
        ("Wake County", "North Carolina", 2098),          # 37 ~1.23M
        ("Allegheny County", "Pennsylvania", 2362),       # 38 ~1.23M
        # 39: Salt Lake County, Utah — Utah has no counties in us_data, SKIPPED
        ("Mecklenburg County", "North Carolina", 2066),   # 40 ~1.21M
        ("Contra Costa County", "California", 309),       # 41 ~1.17M
        ("Fairfax County", "Virginia", 2965),             # 42 ~1.16M
        ("Fulton County", "Georgia", 563),                # 43 ~1.09M
        # 44: Montgomery County, Maryland — Maryland has no counties in us_data, SKIPPED
        ("Pima County", "Arizona", 223),                  # 45 ~1.08M
        ("Duval County", "Florida", 451),                 # 46 ~1.06M
        ("Denton County", "Texas", 2700),                 # 47 ~1.05M
        ("Fresno County", "California", 312),             # 48 ~1.02M
        ("Westchester County", "New York", 2004),         # 49 ~1.01M
        ("Gwinnett County", "Georgia", 570),              # 50 ~1.00M
        ("Honolulu County", "Hawaii", 664),               # 51 ~998K
        # 52: St. Louis County, Missouri — Missouri has no counties in us_data, SKIPPED
        # 53: Capitol (Hartford) County, Connecticut — not listed in us_data CT counties, SKIPPED
        ("Marion County", "Indiana", 862),                # 54 ~982K
        ("Bergen County", "New Jersey", 1892),            # 55 ~979K
        # 56: Prince George's County, Maryland — Maryland has no counties in us_data, SKIPPED
        ("Pinellas County", "Florida", 488),              # 57 ~966K
        ("Fort Bend County", "Texas", 2718),              # 58 ~958K
        ("Erie County", "New York", 1959),                # 59 ~951K
        ("Pierce County", "Washington", 3096),            # 60 ~941K
        ("DuPage County", "Illinois", 733),               # 61 ~937K
        # 62: Milwaukee County, Wisconsin — Wisconsin has no counties in us_data, SKIPPED
        ("Kern County", "California", 317),               # 63 ~923K
        ("Hidalgo County", "Texas", 2747),                # 64 ~915K
        ("Shelby County", "Tennessee", 2623),             # 65 ~911K
        ("Middlesex County", "New Jersey", 1902),         # 66 ~890K
        ("Macomb County", "Michigan", 1397),              # 67 ~886K
        ("Essex County", "New Jersey", 1897),             # 68 ~882K
        ("Worcester County", "Massachusetts", 1347),      # 69 ~881K
        ("Montgomery County", "Pennsylvania", 2406),      # 70 ~879K
        ("El Paso County", "Texas", 2710),                # 71 ~876K
        ("Snohomish County", "Washington", 2),            # 72 ~864K
        ("Lee County", "Florida", 471),                   # 73 ~861K
        ("Polk County", "Florida", 489),                  # 74 ~853K
        # 75: Baltimore County, Maryland — Maryland has no counties in us_data, SKIPPED
        ("Hamilton County", "Ohio", 2190),                # 76 ~837K
        ("Ventura County", "California", 358),            # 77 ~835K
        ("San Francisco County", "California", 340),      # 78 ~828K
        ("Essex County", "Massachusetts", 1338),          # 79 ~824K
        # 80: Oklahoma County, Oklahoma — Oklahoma has no counties in us_data, SKIPPED
        ("San Joaquin County", "California", 341),        # 81 ~816K
        # 82: Multnomah County, Oregon — Oregon has no counties in us_data, SKIPPED
        # 83: Jefferson County, Kentucky — Kentucky has no counties in us_data, SKIPPED
        ("Suffolk County", "Massachusetts", 1346),        # 84 ~793K
        ("Cobb County", "Georgia", 536),                  # 85 ~788K
        ("DeKalb County", "Georgia", 547),                # 86 ~770K
        ("El Paso County", "Colorado", 382),              # 87 ~753K
        ("Monroe County", "New York", 1972),              # 88 ~752K
        ("Montgomery County", "Texas", 2809),             # 89 ~750K
        # 90: Utah County, Utah — Utah has no counties in us_data, SKIPPED
        ("San Mateo County", "California", 343),          # 91 ~743K
        ("Norfolk County", "Massachusetts", 1344),        # 92 ~741K
        ("Hudson County", "New Jersey", 1899),            # 93 ~736K
        ("Davidson County", "Tennessee", 2563),           # 94 ~730K
        ("Denver County", "Colorado", 377),               # 95 ~729K
        ("Williamson County", "Texas", 2885),             # 96 ~727K
        # 97: Jackson County, Missouri — Missouri has no counties in us_data, SKIPPED
        ("Lake County", "Illinois", 760),                 # 98 ~719K
        ("Will County", "Illinois", 810),                 # 99 ~709K
        ("District of Columbia", "Columbia", 436),        # 100 ~702K
    ]

    coastal_counties = [
        # county_name, state, county_id

        # --- GULF COAST ---
        # Alabama
        ("Baldwin County",                      "Alabama",        120),
        ("Mobile County",                       "Alabama",        167),

        # Florida (Gulf)
        ("Escambia County",                     "Florida",        452),
        ("Santa Rosa County",                   "Florida",        493),
        ("Okaloosa County",                     "Florida",        482),
        ("Walton County",                       "Florida",        502),
        ("Bay County",                          "Florida",        439),
        ("Gulf County",                         "Florida",        458),
        ("Franklin County",                     "Florida",        454),
        ("Wakulla County",                      "Florida",        501),
        ("Jefferson County",                    "Florida",        468),
        ("Taylor County",                       "Florida",        498),
        ("Dixie County",                        "Florida",        450),
        ("Levy County",                         "Florida",        473),
        ("Citrus County",                       "Florida",        445),
        ("Hernando County",                     "Florida",        462),
        ("Pasco County",                        "Florida",        487),
        ("Pinellas County",                     "Florida",        488),
        ("Hillsborough County",                 "Florida",        464),
        ("Manatee County",                      "Florida",        476),
        ("Sarasota County",                     "Florida",        494),
        ("Charlotte County",                    "Florida",        444),
        ("Lee County",                          "Florida",        471),
        ("Collier County",                      "Florida",        447),

        # Texas (Gulf)
        ("Orange County",                       "Texas",          2820),
        ("Jefferson County",                    "Texas",          2762),
        ("Chambers County",                     "Texas",          2675),
        ("Galveston County",                    "Texas",          2723),
        ("Harris County",                       "Texas",          2740),
        ("Brazoria County",                     "Texas",          2659),
        ("Matagorda County",                    "Texas",          2800),
        ("Wharton County",                      "Texas",          2880),
        ("Jackson County",                      "Texas",          2759),
        ("Victoria County",                     "Texas",          2874),
        ("Calhoun County",                      "Texas",          2668),
        ("Refugio County",                      "Texas",          2835),
        ("Aransas County",                      "Texas",          2643),
        ("San Patricio County",                 "Texas",          2844),
        ("Nueces County",                       "Texas",          2817),
        ("Kleberg County",                      "Texas",          2776),
        ("Kenedy County",                       "Texas",          2770),
        ("Willacy County",                      "Texas",          2884),
        ("Cameron County",                      "Texas",          2670),

        # --- ATLANTIC COAST ---
        # Florida (Atlantic)
        ("Nassau County",                       "Florida",        481),
        ("Duval County",                        "Florida",        451),
        ("St. Johns County",                    "Florida",        491),
        ("Flagler County",                      "Florida",        453),
        ("Volusia County",                      "Florida",        500),
        ("Brevard County",                      "Florida",        441),
        ("Indian River County",                 "Florida",        466),
        ("St. Lucie County",                    "Florida",        492),
        ("Martin County",                       "Florida",        478),
        ("Palm Beach County",                   "Florida",        486),
        ("Broward County",                      "Florida",        442),
        ("Miami Dade County",                   "Florida",        479),
        ("Monroe County",                       "Florida",        480),

        # Georgia
        ("Camden County",                       "Georgia",        523),
        ("Glynn County",                        "Georgia",        566),
        ("McIntosh County",                     "Georgia",        598),
        ("Liberty County",                      "Georgia",        592),
        ("Bryan County",                        "Georgia",        518),
        ("Chatham County",                      "Georgia",        528),

        # North Carolina
        ("Brunswick County",                    "North Carolina", 2016),
        ("New Hanover County",                  "North Carolina", 2071),
        ("Pender County",                       "North Carolina", 2077),
        ("Onslow County",                       "North Carolina", 2073),
        ("Carteret County",                     "North Carolina", 2022),
        ("Jones County",                        "North Carolina", 2058),
        ("Craven County",                       "North Carolina", 2031),
        ("Pamlico County",                      "North Carolina", 2075),
        ("Beaufort County",                     "North Carolina", 2013),
        ("Hyde County",                         "North Carolina", 2054),
        ("Dare County",                         "North Carolina", 2034),
        ("Tyrrell County",                      "North Carolina", 2095),
        ("Washington County",                   "North Carolina", 2100),
        ("Bertie County",                       "North Carolina", 2014),
        ("Chowan County",                       "North Carolina", 2027),
        ("Perquimans County",                   "North Carolina", 2078),
        ("Pasquotank County",                   "North Carolina", 2076),
        ("Camden County",                       "North Carolina", 2021),
        ("Currituck County",                    "North Carolina", 2033),

        # Virginia
        ("Westmoreland County",                 "Virginia",       3028),
        ("Northumberland County",               "Virginia",       3000),
        ("Lancaster County",                    "Virginia",       2987),
        ("Middlesex County",                    "Virginia",       2995),
        ("Mathews County",                      "Virginia",       2993),
        ("Gloucester County",                   "Virginia",       2972),
        ("James City",                          "Virginia",       2983),
        ("York County",                         "Virginia",       3031),
        ("Newport News",                        "Virginia",       3055),
        ("Hampton",                             "Virginia",       3047),
        ("Norfolk",                             "Virginia",       3056),
        ("Portsmouth",                          "Virginia",       3060),
        ("Chesapeake",                          "Virginia",       3037),
        ("Virginia Beach",                      "Virginia",       3067),
        ("Accomack County",                     "Virginia",       2937),
        ("Northampton County",                  "Virginia",       2999),

        # New York
        ("Westchester County",                  "New York",       2004),
        ("Bronx County",                        "New York",       1947),
        ("New York County",                     "New York",       1975),
        ("Kings County",                        "New York",       1968),
        ("Queens County",                       "New York",       1985),
        ("Richmond County",                     "New York",       1987),
        ("Nassau County",                       "New York",       1974),
        ("Suffolk County",                      "New York",       1996),

        # New Jersey
        ("Bergen County",                       "New Jersey",     1892),
        ("Hudson County",                       "New Jersey",     1899),
        ("Middlesex County",                    "New Jersey",     1902),
        ("Monmouth County",                     "New Jersey",     1903),
        ("Ocean County",                        "New Jersey",     1905),
        ("Atlantic County",                     "New Jersey",     1891),
        ("Cape May County",                     "New Jersey",     1895),

        # Massachusetts
        ("Essex County",                        "Massachusetts",  1338),
        ("Suffolk County",                      "Massachusetts",  1346),
        ("Norfolk County",                      "Massachusetts",  1344),
        ("Plymouth County",                     "Massachusetts",  1345),
        ("Barnstable County",                   "Massachusetts",  1334),
        ("Dukes County",                        "Massachusetts",  1337),
        ("Nantucket County",                    "Massachusetts",  1343),
        ("Bristol County",                      "Massachusetts",  1336),

        # Connecticut
        ("Fairfield County",                    "Connecticut",    425),
        ("New Haven County",                    "Connecticut",    429),
        ("Middlesex County",                    "Connecticut",    428),
        ("New London County",                   "Connecticut",    430),

        # --- PACIFIC COAST ---
        # California
        ("Del Norte County",                    "California",     310),
        ("Humboldt County",                     "California",     314),
        ("Mendocino County",                    "California",     325),
        ("Sonoma County",                       "California",     351),
        ("Marin County",                        "California",     323),
        ("San Francisco County",                "California",     340),
        ("San Mateo County",                    "California",     343),
        ("Santa Cruz County",                   "California",     346),
        ("Monterey County",                     "California",     329),
        ("San Luis Obispo County",              "California",     342),
        ("Santa Barbara County",                "California",     344),
        ("Ventura County",                      "California",     358),
        ("Los Angeles County",                  "California",     321),
        ("Orange County",                       "California",     332),
        ("San Diego County",                    "California",     339),

        # Washington (Pacific/Puget Sound)
        ("Whatcom County",                      "Washington",     3105),
        ("Skagit County",                       "Washington",     3098),
        ("Island County",                       "Washington",     3085),
        ("Snohomish County",                    "Washington",     2),
        ("King County",                         "Washington",     118),
        ("Pierce County",                       "Washington",     3096),
        ("Kitsap County",                       "Washington",     3087),
        ("Mason County",                        "Washington",     3092),
        ("Thurston County",                     "Washington",     3102),
        ("Grays Harbor County",                 "Washington",     3084),
        ("Pacific County",                      "Washington",     3094),
        ("Wahkiakum County",                    "Washington",     3103),
        ("Clallam County",                      "Washington",     3075),
        ("Jefferson County",                    "Washington",     3086),

        # Hawaii (Pacific)
        ("Hawaii County",                       "Hawaii",         663),
        ("Honolulu County",                     "Hawaii",         664),
        ("Kauai County",                        "Hawaii",         666),
        ("Maui County",                         "Hawaii",         667),

        # Alaska (Pacific/Arctic)
        ("Aleutians East Borough",              "Alaska",         186),
        ("Aleutians West Census Area",          "Alaska",         187),
        ("Anchorage Borough",                   "Alaska",         188),
        ("Bethel Census Area",                  "Alaska",         189),
        ("Bristol Bay Borough",                 "Alaska",         190),
        ("Dillingham Census Area",              "Alaska",         192),
        ("Haines Borough",                      "Alaska",         194),
        ("Hoonah Angoon Census Area",           "Alaska",         3351),
        ("Juneau Borough",                      "Alaska",         195),
        ("Kenai Peninsula Borough",             "Alaska",         196),
        ("Ketchikan Gateway Borough",           "Alaska",         197),
        ("Kodiak Island Borough",               "Alaska",         198),
        ("Kusilvak Census Area",                "Alaska",         209),
        ("Lake and Peninsula Borough",          "Alaska",         199),
        ("Matanuska Susitna Borough",           "Alaska",         200),
        ("Nome Census Area",                    "Alaska",         201),
        ("North Slope Borough",                 "Alaska",         202),
        ("Northwest Arctic Borough",            "Alaska",         203),
        ("Petersburg Borough",                  "Alaska",         3352),
        ("Prince of Wales Hyder Census Area",   "Alaska",         204),
        ("Sitka Borough",                       "Alaska",         205),
        ("Skagway Borough",                     "Alaska",         206),
        ("Wrangell Borough",                    "Alaska",         210),
        ("Yakutat Borough",                     "Alaska",         211),
    ]


    headers = {
        "authority": "www.redfin.com",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7,tr;q=0.6,hu;q=0.5",
        "cache-control": "no-cache",
        "pragma": "no-cache",
        "priority": "u=0, i",
        "referer": "https://www.redfin.com/",
        "sec-ch-ua": '"Google Chrome";v="147", "Not.A/Brand";v="8", "Chromium";v="147"',
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-platform": '"Android"',
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "same-origin",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Mobile Safari/537.36",
    }

    final_ads = []
    # Build a lookup: county name -> state code
    state_code_lookup = {state: data["code"] for state, data in us_data.items()}

    def safe_text(el, default=None):
        return el.get_text(strip=True) if el else default

    def safe_attr(el, attr, default=None):
        return el.get(attr) if el and el.has_attr(attr) else default

    # for state, state_data in us_data.items():
    #     state_code = state_code_lookup[state]

    #     for county, county_id in state_data["counties"].items():

    for county, state, county_id in top_100_counties:
        state_code = state_code_lookup[state]
        for page in range(1, 3):
            url = f'https://www.redfin.com/county/{county_id}/{state_code}/{county.replace(" ", "-")}/filter/sort=lo-days/page-{page}'
            r = requests.get(url, headers=headers)
            soup = BeautifulSoup(r.content, 'lxml')
            ads = soup.find_all('div', class_='bp-mobileListHomeCard')

            for ad in ads:
                state = state
                state_code = state_code
                county = county
                relative_url = safe_attr(ad.find('a'), 'href')
                city = relative_url.split('/')[2] if relative_url else None
                img = safe_attr(ad.find('img'), 'src')
                price = safe_text(ad.find('div', class_='bp-Homecard__Price'))
                bedrooms = safe_text(ad.find('span', class_='bp-Homecard__Stats--beds'))
                bathrooms = safe_text(ad.find('span', class_='bp-Homecard__Stats--baths'))
                area = safe_text(ad.find('span', class_='bp-Homecard__Stats--sqft'))
                address = safe_text(ad.find('a'))
                final_ads.append({'state': state, 'county': county, 'state_code': state_code,
                                'city': city, 'img': img, 'price': price, 'bedrooms': bedrooms,
                                'bathrooms': bathrooms, 'area': area, 'address': address,
                                'relative_url': relative_url})

    df = pd.DataFrame(final_ads)
    df = df.dropna(subset=['price'])
    return df

def clean(df_in : pd.DataFrame) -> pd.DataFrame:
    df = df_in.copy()
    df = df[~df.price.str.contains("Unknown")]
    df.loc[df.area.str.contains('—', na=False), 'area'] = None
    df.loc[df.bedrooms.str.contains('—', na=False), 'bedrooms'] = None
    df.loc[df.bathrooms.str.contains('—', na=False), 'bathrooms'] = None
    df["price"] = pd.to_numeric(df["price"].astype(str).str.extract(r'(\d[\d,]*)')[0].str.replace(',', '', regex=False),    errors="coerce")
    df["bedrooms"] = df.bedrooms.apply(lambda x: int(x.split()[0]) if x else None)
    df["bathrooms"] = df.bathrooms.apply(lambda x: float(x.split()[0]) if x else None)
    df["unit"] = df.area.apply(lambda x: 'sq ft' if x and 'sq ft' in x else 'acre')
    df["area"] = pd.to_numeric(df["area"].astype(str).str.extract(r'(\d[\d,\.]*)')[0].str.replace(',', '', regex=False), errors="coerce")
    df["url"] = "https://www.redfin.com" + df["relative_url"]
    df["area_m2"] = df.apply(lambda row: round(row.area * 0.092903, 2) if row.unit == 'sq ft' else round(row.area * 4046.86, 2) if row.unit == 'acre' else None, axis=1)
    df["price_per_m2"] = df.apply(lambda row: round(row.price / row.area_m2, 2) if row.price and row.area_m2 else None, axis=1)
    df["source"] = "redfin"
    df["query_date"] = pd.Timestamp.now().strftime("%Y-%m-%d")

    return df.reset_index(drop=True)

def save(df:pd.DataFrame):
    df.to_csv("usa.csv", index=False, encoding="utf-8-sig", sep=";")
#%%