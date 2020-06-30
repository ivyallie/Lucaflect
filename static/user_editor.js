let add_web_presence = function() {
  let web_presence_list = document.getElementById('web_presence_list');
  let template = document.getElementById('web_presence_entry');
  let clone = template.content.cloneNode(true);
  web_presence_list.appendChild(clone);
};

let make_user = function () {
    let name = document.getElementById('name');
    let email = document.getElementById('email');
    let bio = document.getElementById('bio');
    let web_presence_list = document.getElementById('web_presence_list');
    let web_presence_links = [];
    let wp_li_elements = web_presence_list.querySelectorAll('li');
    let portrait = document.getElementById('portrait');
    let portrait_filepath = portrait.getAttribute('src');
    let portrait_filename = portrait_filepath.replace(/^.*[\\\/]/, '');
    let admin = document.getElementById('admin_user');
    let group = '';
    let username_input = document.getElementById('username');
    let username = username_input.value;
    if (admin) {
        if (admin.checked) {
            group='admin'
        } else { group='user'}};

    for (i=0; i<wp_li_elements.length; i++) {
        let li = wp_li_elements[i];
        let link_name = li.querySelector('.wp_title');
        let link_url = li.querySelector('.wp_url');
        let link = {
            'link_name' : link_name.value,
            'link_url' : link_url.value
        };
        web_presence_links.push(link)
    };
    let user = {
        'name' : name.value,
        'email' : email.value,
        'bio' : bio.value,
        'web_links' : web_presence_links,
        'portrait': portrait_filename,
        'group': group,
        'username':username,
    };

    return user
};

let applyChanges = function (name) {
    let user = make_user();
    let json_user = JSON.stringify(user);
    fetch('/update_user/'+name, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: json_user,
    } )
    .then(response => {
            if (!response.ok) {
                throw new Error('Something went wrong');
            }
            return response.json();
        })
        .then(result => {
            let redirect = result['redirect'];
            window.location.replace(redirect);
        })
        .catch((error) => { alert(error);})

};

let populateLinks = function (links) {
    //console.log(links)
     let web_presence_list = document.getElementById('web_presence_list');
     let template = document.getElementById('web_presence_entry');
    for (i=0; i<links.length; i++) {
          let clone = template.content.cloneNode(true);
          let link_name = clone.querySelector('.wp_title');
        let link_url = clone.querySelector('.wp_url');
        link_name.value = links[i]['link_name'];
        link_url.value = links[i]['link_url'];
  web_presence_list.appendChild(clone);
    }


}