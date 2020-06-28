let remove_from_list = function (button) {
     let parent = get_parent_of_type(button,'LI')
     parent.remove()
    };

let view_comic_image = function (button) {
    let li = get_parent_of_type(button,'LI');
    let source_url = li.getAttribute('data-imgurl');
    let filename = source_url.replace(/^.*[\\\/]/, '');
    let access_url = "/uploads/"+filename;
    window.open(access_url,'_blank')
}

let get_parent_of_type = function (element,tag) {
    let parent = element.parentElement;
    while (!(parent.tagName===tag)) {
        parent = parent.parentElement;
    }
    return parent
}

let show_hidden = function (element_id, button=button) {
    let element = document.getElementById(element_id);
    console.log(element);
    element.classList.remove('hide');
    if (button) {
        button.classList.add('hide');
    }
}