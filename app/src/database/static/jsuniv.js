/*Javascript file that contains the general scripts for selecting and setting the class and sublasses of supply*/
// function subclassSet() {
//     recCOS = document.getElementById("inputCOS").value;

//     document.getElementById("inputCOSSub1").style.display = "none";
//     document.getElementById("inputCOSSub2").style.display = "none";
//     document.getElementById("inputCOSSub3").style.display = "none";
//     document.getElementById("inputCOSSub4").style.display = "none";
//     document.getElementById("inputCOSSub5").style.display = "none";
//     document.getElementById("inputCOSSub6").style.display = "none";
//     document.getElementById("inputCOSSub7").style.display = "none";
//     document.getElementById("inputCOSSub8").style.display = "none";
//     document.getElementById("inputCOSSub9").style.display = "none";
//     document.getElementById("inputCOSSub4Sub").style.display = "none";
//     document.getElementById("inputCOSSub8Sub").style.display = "none";
//     document.getElementById("inputCOSSub9Sub").style.display = "none";

//     switch (recCOS) {
//         case 'Propellants and Fuels': {
//             document.getElementById("inputCOSSub1").style.display = "block";
//             break;
//         }
//         case 'Crew Provisions': {
//             document.getElementById("inputCOSSub2").style.display = "block";
//             break;
//         }
//         case 'Crew Operations': {
//             document.getElementById("inputCOSSub3").style.display = "block";
//             break;
//         }
//         case 'Maintenence and Upkeep': {
//             document.getElementById("inputCOSSub4").style.display = "block";
//             break;
//         }
//         case 'Stowage and Restraint': {
//             document.getElementById("inputCOSSub5").style.display = "block";
//             break;
//         }
//         case 'Exploration and Research': {
//             document.getElementById("inputCOSSub6").style.display = "block";
//             break;
//         }
//         case 'Waste and Disposal': {
//             document.getElementById("inputCOSSub7").style.display = "block";
//             break;
//         }
//         case 'Habitation and Infrastructure': {
//             document.getElementById("inputCOSSub8").style.display = "block";
//             break;
//         }
//         case 'Transportation and Carriers': {
//             document.getElementById("inputCOSSub9").style.display = "block";
//             break;
//         }
//     }
// }

// function subSelect4() {
//     sub4 = document.getElementById("inputCOSSub4").value;
//     if (sub4 === "Spares and Repair Parts") {
//         document.getElementById("inputCOSSub4Sub").style.display = "block";
//     }
// }

// function subSelect8() {
//     sub8 = document.getElementById("inputCOSSub8").value;
//     if (sub8 === "Robotic Systems") {
//         document.getElementById("inputCOSSub8Sub").style.display = "block";
//     }
// }

// function subSelect9() {
//     sub9 = document.getElementById("inputCOSSub9").value;
//     if (sub9 === "Propulsive Elements") {
//         document.getElementById("inputCOSSub9Sub").style.display = "block";

//     }
// }

// function setCOS() {
//     switch (classOS) {
//         case 1: {
//             switch (document.getElementById("inputCOSSub1").value) {
//                 case 'Cryogens' : {
//                     classOS = 101;
//                     break;
//                 }
//                 case 'Hypergols': {
//                     classOS = 102;
//                     break;
//                 }
//                 case 'Nuclear Fuel' : {
//                     classOS = 103;
//                     break;
//                 }
//                 case 'Petroleum Fuels': {
//                     classOS = 104;
//                     break;
//                 }
//                 case 'Other Fuels': {
//                     classOS = 105;
//                     break;
//                 }
//             }
//             break;
//         }
//         case 2: {
//             switch (document.getElementById("inputCOSSub2").value) {
//                 case 'Water and Support Equipment' : {
//                     classOS = 201;
//                     break;
//                 }
//                 case 'Food and Support Equipment' : {
//                     classOS = 202;
//                     break;
//                 }
//                 case 'Gases' : {
//                     classOS = 203;
//                     break;
//                 }
//                 case 'Hygiene Items' : {
//                     classOS = 204;
//                     break;
//                 }
//                 case 'Clothing' : {
//                     classOS = 205;
//                     break;
//                 }
//                 case 'Personal Items' : {
//                     classOS = 206;
//                     break;
//                 }
//             }
//             break;
//         }
//         case 3: {
//             switch (document.getElementById("inputCOSSub3").value) {
//                 case 'Office Equipment and Supplies' : {
//                     classOS = 301;
//                     break;
//                 }
//                 case 'EVA Equipment and Consumables' : {
//                     classOS = 302;
//                     break;
//                 }
//                 case 'Health Equipment and Consumables' : {
//                     classOS = 303;
//                     break;
//                 }
//                 case 'Safety Equipment' : {
//                     classOS = 304;
//                     break;
//                 }
//                 case 'Communications Equipment' : {
//                     classOS = 305;
//                     break;
//                 }
//                 case 'Computers and Support Equipment' : {
//                     classOS = 306;
//                     break;
//                 }
//             }
//             break;
//         }
//         case 4: {
//             switch (document.getElementById("inputCOSSub4").value) {
//                 case 'Spares and Repair Parts' : {
//                     classOS = 401;
//                     break;
//                 }
//                 case 'Maintenence Tools' : {
//                     classOS = 402;
//                     break;
//                 }
//                 case 'Lubricants and Bulk Chemicals' : {
//                     classOS = 403;
//                     break;
//                 }
//                 case 'Batteries' : {
//                     classOS = 404;
//                     break;
//                 }
//                 case 'Cleaning Equipment and Consumables' : {
//                     classOS = 405;
//                     break;
//                 }
//             }
//             break;
//         }
//         case 401: {
//             switch (document.getElementById("inputCOSSub4Sub").value) {
//                 case 'Spares' : {
//                     classOS = 4011;
//                     break;
//                 }
//                 case 'Repair Parts' : {
//                     classOS = 4012;
//                     break;
//                 }
//             }
//             break;
//         }
//         case 5: {
//             switch (document.getElementById("inputCOSSub5").value) {
//                 case 'Cargo Containers and Restraints' : {
//                     classOS = 501;
//                     break;
//                 }
//                 case 'Inventory Management Equipment' : {
//                     classOS = 502;
//                     break;
//                 }
//             }
//             break;
//         }
//         case 6: {
//             switch (document.getElementById("inputCOSSub6").value) {
//                 case 'Science Payloads and Instruments' : {
//                     classOS = 601;
//                     break;
//                 }
//                 case 'Field Equipment' : {
//                     classOS = 602;
//                     break;
//                 }
//                 case 'Samples' : {
//                     classOS = 603;
//                     break;
//                 }
//             }
//             break;
//         }
//         case 7: {
//             switch (document.getElementById("inputCOSSub7").value) {
//                 case 'Waste' : {
//                     classOS = 701;
//                     break;
//                 }
//                 case 'Waste Management Equipment' : {
//                     classOS = 702;
//                     break;
//                 }
//                 case 'Failed Pairs' : {
//                     classOS = 703;
//                     break;
//                 }
//             }
//             break;
//         }
//         case 8: {
//             switch (document.getElementById("inputCOSSub8").value) {
//                 case 'Habitation Facilities' : {
//                     classOS = 801;
//                     break;
//                 }
//                 case 'Surface Mobility Systems' : {
//                     classOS = 802;
//                     break;
//                 }
//                 case 'Power Systems' : {
//                     classOS = 803;
//                     break;
//                 }
//                 case 'Robotic Systems' : {
//                     classOS = 804;
//                     break;
//                 }
//                 case 'Resource Utilization Systems' : {
//                     classOS = 805;
//                     break;
//                 }
//                 case 'Orbiting Service Systems' : {
//                     classOS = 806;
//                     break;
//                 }
//             }
//             break;
//         }
//         case 804: {
//             switch (document.getElementById("inputCOSSub8Sub").value) {
//                 case 'Science Robotics' : {
//                     classOS = 8041;
//                     break;
//                 }
//                 case 'Construction/Maintenence Robotics' : {
//                     classOS = 8042;
//                     break;
//                 }
//             }
//             break;
//         }
//         case 9: {
//             switch (document.getElementById("inputCOSSub9").value) {
//                 case 'Carriers, Non-propulsive Elements' : {
//                     classOS = 901;
//                     break;
//                 }
//                 case 'Propulsive Elements' : {
//                     classOS = 902;
//                     break;
//                 }
//             }
//             break;
//         }
//         case 902: {
//             switch (document.getElementById("inputCOSSub9Sub").value) {
//                 case 'Launch Vehicles' : {
//                     classOS = 9021;
//                     break;
//                 }
//                 case 'Upper Stages/In-Space Propulsion Systems' : {
//                     classOS = 9022;
//                     break;
//                 }
//                 case 'Descent Stages' : {
//                     classOS = 9023;
//                     break;
//                 }
//                 case 'Ascent Stages' : {
//                     classOS = 9024;
//                     break;
//                 }
//             }
//             break;
//         }

//     }
// }


/*Javascript file that contains the general scripts for selecting and setting the class and sublasses of supply*/
function subclassSet(modalType){
    recCOS = $("#" + modalType + "InputCOS").val();
  
    $("#" + modalType + "InputCOSSub1").hide();
    $("#" + modalType + "InputCOSSub2").hide();
    $("#" + modalType + "InputCOSSub3").hide();
    $("#" + modalType + "InputCOSSub4").hide();
    $("#" + modalType + "InputCOSSub5").hide();
    $("#" + modalType + "InputCOSSub6").hide();
    $("#" + modalType + "InputCOSSub7").hide();
    $("#" + modalType + "InputCOSSub8").hide();
    $("#" + modalType + "InputCOSSub9").hide();
    $("#" + modalType + "InputCOSSub4Sub").hide();
    $("#" + modalType + "InputCOSSub8Sub").hide();
    $("#" + modalType + "InputCOSSub9Sub").hide();
  
    switch(recCOS){
      case 'Propellants and Fuels':{
        $("#" + modalType + "InputCOSSub1").show();
        break;
      }
      case 'Crew Provisions':{
        $("#" + modalType + "InputCOSSub2").show();
        break;
      }
      case 'Crew Operations':{
        $("#" + modalType + "InputCOSSub3").show();
        break;
      }
      case 'Maintenence and Upkeep':{
        $("#" + modalType + "InputCOSSub4").show();
        break;
      }
      case 'Stowage and Restraint':{
        $("#" + modalType + "InputCOSSub5").show();
        break;
      }
      case 'Exploration and Research':{
        $("#" + modalType + "InputCOSSub6").show();
        break;
      }
      case 'Waste and Disposal':{
        $("#" + modalType + "InputCOSSub7").show();
        break;
      }
      case 'Habitation and Infrastructure':{
        $("#" + modalType + "InputCOSSub8").show();
        break;
      }
      case 'Transportation and Carriers':{
        $("#" + modalType + "InputCOSSub9").show();
        break;
      }
    }
  }
  
  function subSelect4(modalType){
    sub4 = $("#" + modalType + "InputCOSSub4").val();
    if(sub4 == "Spares and Repair Parts"){
      $("#" + modalType + "InputCOSSub4Sub").show();
    }
  }
  
  function subSelect8(modalType){
    sub8 = $("#" + modalType + "InputCOSSub8").val();
    if(sub8 == "Robotic Systems"){
      $("#" + modalType + "InputCOSSub8Sub").show();
    }
  }
  
  function subSelect9(modalType){
    sub9 = $("#" + modalType + "InputCOSSub9").val();
    if(sub9 == "Propulsive Elements"){
      $("#" + modalType + "InputCOSSub9Sub").show();
  
    }
  }
  
  function setCOS(modalType){
    switch(classOS){
      case 1: {
        switch($("#" + modalType + "InputCOSSub1").val()){
          case 'Cryogens' : {classOS = 101; break;}
          case 'Hypergols': {classOS = 102; break;}
          case 'Nuclear Fuel' : {classOS = 103; break;}
          case 'Petroleum Fuels':{ classOS = 104; break;}
          case 'Other Fuels': {classOS = 105; break;}
      } break; }
      case 2: {
        switch($("#" + modalType + "InputCOSSub2").val()){
          case 'Water and Support Equipment' : {classOS = 201; break;}
          case 'Food and Support Equipment' : {classOS = 202; break;}
          case 'Gases' : {classOS = 203; break;}
          case 'Hygiene Items' : {classOS = 204; break;}
          case 'Clothing' : {classOS = 205; break;}
          case 'Personal Items' : {classOS = 206; break;}
        } break; }
      case 3: {
        switch($("#" + modalType + "InputCOSSub3").val()){
          case 'Office Equipment and Supplies' : {classOS = 301; break;}
          case 'EVA Equipment and Consumables' : {classOS = 302; break;}
          case 'Health Equipment and Consumables' : {classOS = 303; break;}
          case 'Safety Equipment' : {classOS = 304; break;}
          case 'Communications Equipment' : {classOS = 305; break;}
          case 'Computers and Support Equipment' : {classOS = 306; break;}
        } break; }
      case 4: {
        switch($("#" + modalType + "InputCOSSub4").val()){
          case 'Spares and Repair Parts' : {classOS = 401; break;}
          case 'Maintenence Tools' : {classOS = 402; break;}
          case 'Lubricants and Bulk Chemicals' : {classOS = 403; break;}
          case 'Batteries' : {classOS = 404; break;}
          case 'Cleaning Equipment and Consumables' : {classOS = 405; break;}
        } break; }
      case 401: {
        switch($("#" + modalType + "InputCOSSub4Sub").val()){
          case 'Spares' : {classOS = 4011; break;}
          case 'Repair Parts' : {classOS = 4012; break;}
        } break; }
      case 5: {
        switch($("#" + modalType + "InputCOSSub5").val()){
          case 'Cargo Containers and Restraints' : {classOS = 501; break;}
          case 'Inventory Management Equipment' : {classOS = 502; break;}
        } break; }
      case 6: {
        switch($("#" + modalType + "InputCOSSub6").val()){
          case 'Science Payloads and Instruments' : {classOS = 601; break;}
          case 'Field Equipment' : {classOS = 602; break;}
          case 'Samples' : {classOS = 603; break;}
        } break; }
      case 7: {
        switch($("#" + modalType + "InputCOSSub7").val()){
          case 'Waste' : {classOS = 701; break;}
          case 'Waste Management Equipment' : {classOS = 702; break;}
          case 'Failed Pairs' : {classOS = 703; break;}
        } break; }
      case 8: {
        switch($("#" + modalType + "InputCOSSub8").val()){
          case 'Habitation Facilities' : {classOS = 801; break;}
          case 'Surface Mobility Systems' : {classOS = 802; break;}
          case 'Power Systems' : {classOS = 803; break;}
          case 'Robotic Systems' : {classOS = 804; break;}
          case 'Resource Utilization Systems' : {classOS = 805; break;}
          case 'Orbiting Service Systems' : {classOS = 806; break;}
        } break; }
      case 804: {
        switch($("#" + modalType + "InputCOSSub8Sub").val()){
          case 'Science Robotics' : {classOS = 8041; break;}
          case 'Construction/Maintenence Robotics' : {classOS = 8042; break;}
        } break; }
      case 9: {
        switch($("#" + modalType + "InputCOSSub9").val()){
          case 'Carriers, Non-propulsive Elements' : {classOS = 901; break;}
          case 'Propulsive Elements' : {classOS = 902; break;}
        } break; }
      case 902: {
        switch($("#" + modalType + "InputCOSSub9Sub").val()){
          case 'Launch Vehicles' : {classOS = 9021; break;}
          case 'Upper Stages/In-Space Propulsion Systems' : {classOS = 9022; break;}
          case 'Descent Stages' : {classOS = 9023; break;}
          case 'Ascent Stages' : {classOS = 9024; break;}
        } break; }
  
    }
  }
  