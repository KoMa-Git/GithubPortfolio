function change_name() {
  var x = document.getElementById("nm");
  if (x.type === "hidden") {
    x.type = "text";
    document.getElementById("stg").style.display = "none";
  } else {
    x.type = "hidden";
    document.getElementById("stg").style.display = "inline";
    document.getElementById("name").submit();
  }
}

function change_pass() {
  if (document.getElementById("old_pass").type === "hidden") {
    document.getElementById("old_pass").type = "text";
    document.getElementById("new_pass").type = "text";
  } else {
    document.getElementById("old_pass").type = "hidden";
    document.getElementById("new_pass").type = "hidden";
    document.getElementById("pass").submit();
  }        
}

function del_acc() {
  if (document.getElementById("del").type === "hidden") {
    document.getElementById("del").type = "text";
  } else {
    document.getElementById("del").type = "hidden";
    document.getElementById("del_acc").submit();
  }
}