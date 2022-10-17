function allLetter(input) {
    var cyrillicPattern = /^[А-Яа-яё]+$/i;
    var latinPattern = /^[A-Za-z]+$/i;
    if (cyrillicPattern.test(input) || latinPattern.test(input)) {
        return true;
    } else {
        alert('Name must have alphabet characters only');
        return false;
    }
}

function isNumber(input) {
    var numPattern = /^\d+$/;
    if (numPattern.test(input)) {
        return true;
    } else {
        return false;
    }
}

function searchformValidation() {
    var lastname = document.search.lastname.value;
    var firstname = document.search.firstname.value;
    var middlename = document.search.middlename.value;
    
    if (!allLetter(lastname)) {
        return false;
    }
    
    if (firstname.length > 0 && !allLetter(firstname)) {
        return false;
    }
    
    if (middlename.length > 0 && !allLetter(middlename)) {
        return false;
    }
    
    return true;
}

function uploadformValidation() {
    var lastname = document.updateform.lastname.value;
    var firstname = document.updateform.firstname.value;
    var middlename = document.updateform.middlename.value;
    var year = document.updateform.year.value;
    var page = document.updateform.page.value;
    
    if (!allLetter(lastname)) {
        return false;
    }
    
    if (firstname.length > 0 && !allLetter(firstname)) {
        return false;
    }
    
    if (middlename.length > 0 && !allLetter(middlename)) {
        return false;
    }
    
    if (!isNumber(year)) {
        alert('Year must be a number');
        return false;
    }
    
    if (!isNumber(page)) {
        alert('Page must be a number');
        return false;
    }
    
    return true;
}


function show_image(src, width, height, alt) {
    var img = document.createElement("img");
    img.src = src;
    img.width = width;
    img.height = height;
    img.alt = alt;

    // This next line will just add it to the <body> tag
    document.body.appendChild(img);
}
