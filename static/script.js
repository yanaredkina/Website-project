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
    var lastname = document.registration.lastname.value;
    var firstname = document.registration.firstname.value;
    var middlename = document.registration.middlename.value;
    
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
