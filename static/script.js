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
    
    if (isNaN(year)) {
        alert('Year must be a number');
        return false;
    }
    
    if (isNaN(page)) {
        alert('Page must be a number');
        return false;
    }
    
    return true;
}

function allLetter(name) {
    var letters = /^[А-Яа-яё]+$/i;
    if (letters.test(name)) {
        return true;
    } else {
        alert('Name must have cyrillic alphabet characters only');
        return false;
    }
}
