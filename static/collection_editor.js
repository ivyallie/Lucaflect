let comic_menu = document.getElementById('comic_menu');

        let listComicsByAuthor = function (id) {

            fetch('/getcomics/' + id, {
                method: 'GET',
                headers: {'Content-Type': 'application/json'},
            })
                .then(response => response.json())
                .then(result => {
                    //console.log(result['comics']);
                    let comics = result['comics'];
                    generateMenu(comics);
                    //console.log('Comics:', comics);
                })
                .catch(error => {
                    console.log('Error:', error);
                })

        };

        let getUniqueId = function() {
            return new Date().getTime();
        }

        let listCollections = function() {
            fetch('/getcollections', {
                method: 'GET',
                headers: {'Content-Type':'application/json'},
            })
            .then(response => response.json())
                .then(result => {
                    //console.log(result['comics']);
                    let collections = result['collections'];
                    generateCollectionMenu(collections);
                    //console.log('Comics:', comics);
                })
                .catch(error => {
                    console.log('Error:', error);
                })
        };

        let generateCollectionMenu = function(collections) {
            comic_menu.innerHTML = '';
            for (i=0;i<collections.length;i++) {
                let title = collections[i]["title"];
                let internal_title=collections[i]['internal_title'];
                let url='/collections/'+internal_title;
                createMenuEntry(title,internal_title,link=url, extra_class="collection")
            }
        }

        let createMenuEntry = function(display_title,internal_title,link="",extra_class="") {
            let listing_template = document.getElementById('comic_menu_listing');
            let clone = listing_template.content.cloneNode(deep = true,);
            let name = clone.querySelector('span');
            let viewlink = clone.querySelector('a');
            let how_many = clone.querySelector('div.how_many');
            let expand_option = clone.querySelector('div.expand_option');
            name.innerHTML = display_title;
            name.setAttribute('title', internal_title);
            if (link) {
                viewlink.setAttribute('href', link);
            } else {
                viewlink.remove()
            }

            if (extra_class) {
                //console.log(extra_class);
                let li = clone.querySelector('li');
                li.classList.add(extra_class);
                if (extra_class==='collection') {
                    how_many.remove();
                    setUniqueIDs(expand_option);
                } else if (extra_class==='smartlist') {
                    expand_option.remove();
                    setUniqueIDs(how_many);
                } else {
                    if (expand_option) {
                        expand_option.remove();
                    }
                    if (how_many) {
                        how_many.remove();
                    }

                }
            } else {
                if (how_many) {
                    how_many.remove();
                }
                if (expand_option) {
                    expand_option.remove();
                }

            }

            comic_menu.appendChild(clone)

        };

        let setUniqueIDs = function(parent) {
            let id=getUniqueId();
            parent.querySelector('input').setAttribute('id',id);
            parent.querySelector('label').setAttribute('for',id);
        };

        let listSmartSections = function() {
            let types = [
                {'name':'Recent comics','internal_name':'recent_comics','class':'smartlist'},
                {'name':'Recent collections','internal_name':'recent_collections','class':'smartlist'},
                {'name':'About','internal_name':'about','class':'smart'},
            ];
            comic_menu.innerHTML='';
            for (i=0; i<types.length; i++) {
                createMenuEntry(types[i]['name'],types[i]['internal_name'], link="",extra_class=types[i]['class'])
            }
        };

        let generateMenu = function (comics) {
            let listing_template = document.getElementById('comic_menu_listing');
            comic_menu.innerHTML = '';
            for (c = 0; c < comics.length; c++) {
                createMenuEntry(comics[c]['title'],comics[c]['internal_title'],link='/comic/'+comics[c]['internal_title']);
            }
        };

        let postCollection = function () {
            let title = document.getElementById('title');
            let description = document.getElementById('description');
            let sequence = getComicSequence();
            //console.log(sequence);
            let submit_button = document.getElementById('submit_button');
            let collection_id = null;
            if (submit_button.getAttribute('data-id')) {
                collection_id = submit_button.getAttribute('data-id')
            }

            let collection = {
                'title': title.value,
                'description': description.value,
                'sequence': sequence,
                'id':collection_id
            };

            let collection_json = JSON.stringify(collection);

            fetch('/collection/post', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: collection_json,
            })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Something went wrong');
                    }
                    return response.json();
                })
                .then(result => {
                    //alert(result['redirect']);
                    let redirect = result['redirect'];
                    //console.log(redirect);
                    window.location.replace(redirect);
                })
                .catch((error) => {

                    alert(error);
                })

        };

        let postHomepage = function() {
            let sequence=getHomepageSequence();
            let sequence_json = JSON.stringify(sequence);
            //console.log(sequence);
            fetch('/admin/homepage/modify', {
                method:'POST',
                headers: {'Content-Type': 'application/json'},
                body: sequence_json,
            })
                 .then(response => {
                    if (!response.ok) {
                        throw new Error('Something went wrong');
                    }
                    return response.json();
                })
                .then(result => {
                    //let redirect = result['redirect'];
                    //window.location.replace(redirect);
                    //alert('Successfully updated homepage!')
                    window.location.reload()
                })
                .catch((error) => {

                    alert(error);
                })
        };

        let getHomepageSequence = function() {
            let collection_sequence = document.getElementById('collection_sequence');
            let list_elements = collection_sequence.querySelectorAll('li');
            let homepage_sequence = [];
            for (i=0; i<list_elements.length; i++) {
                let classes = list_elements[i].classList;
                let titleElement = list_elements[i].querySelector('span');
                let title = titleElement.getAttribute('title');
                let display_title = titleElement.innerHTML;


                if (classes.contains('collection')) {
                    let expand = list_elements[i].querySelector('div.expand_option input:checked') !== null | 0;
                    let collection = {
                        'internal_title':title,
                        'title':display_title,
                        'type':'collection',
                        'expand':expand.toString()
                    };
                    homepage_sequence.push(collection)
                } else if (classes.contains('smartlist')) {
                    let how_many = list_elements[i].querySelector('div.how_many input').value;
                    let smartlist = {
                        'internal_title':title,
                        'title':display_title,
                        'type':'smartlist',
                        'how_many':how_many
                    };
                    homepage_sequence.push(smartlist);
                } else if (classes.contains('smart')) {
                    let smart = {
                        'internal_title':title,
                        'title':display_title,
                        'type':'smart'
                    };
                    homepage_sequence.push(smart);
                } else {
                    let comic = {
                        'internal_title':title,
                        'title':display_title,
                        'type':'comic'
                    };
                    homepage_sequence.push(comic);
                }
            }
            return homepage_sequence
        };

        let inList = function(str,list) {
            return ((list.indexOf(str))>=0)
        };

        let getComicSequence = function () {
            //console.log('Image list');
            let collection_sequence = document.getElementById('collection_sequence');
            let list_elements = collection_sequence.querySelectorAll('li');
            let comic_sequence = [];
            for (i = 0; i < list_elements.length; i++) {
                let title_element = list_elements[i].querySelector('span');
                let internal_title = title_element.getAttribute('title');
                comic_sequence.push(internal_title);
            }
            return comic_sequence
        };

        let initialize_editor = function (sequence) {
        let sequence_editor = document.getElementById('collection_sequence');
        let listing_template = document.getElementById('comic_menu_listing');
        //console.log(sequence);
        //console.log(typeof(sequence))
        for (i=0;i<sequence.length;i++) {
            let clone = listing_template.content.cloneNode(deep = true,);
            let name = clone.querySelector('span');
            let viewlink = clone.querySelector('a');
            name.innerHTML = sequence[i]['title'];
            name.setAttribute('title', sequence[i]['internal_title']);
            viewlink.setAttribute('href', '/comic/' + sequence[i]['internal_title']);
            sequence_editor.appendChild(clone)
        }


    }

    let initialize_homepage_editor = function (sequence) {
            //console.log('homepage editor intializing');
       let sequence_editor = document.getElementById('collection_sequence');
       let listing_template = document.getElementById('comic_menu_listing');
       for (i=0;i<sequence.length;i++) {
           let clone = listing_template.content.cloneNode(deep = true,);
           let name = clone.querySelector('span');
           let viewlink = clone.querySelector('a');
           let how_many = clone.querySelector('div.how_many');
           let how_many_input = how_many.querySelector('input');
           let expand_option = clone.querySelector('div.expand_option');
           let expand_option_input = expand_option.querySelector('input');
           name.innerHTML = sequence[i]['title'];
           name.setAttribute('title', sequence[i]['internal_title']);
           let li = clone.querySelector('li');
           //console.log(li.classList);
           let attributes = li.classList;
           if (sequence[i]['type']==='smartlist') {
               attributes.add('smart');
               expand_option.remove();
               viewlink.remove();
               how_many_input.value = sequence[i]['how_many'];
               console.log(sequence[i]['how_many'])
           } else if  (sequence[i]['type']==='smart') {
                attributes.add('smart');
               how_many.remove();
               expand_option.remove();
               viewlink.remove();
           }
           else if (sequence[i]['type']==='collection') {
               attributes.add('collection')
               let expand = parseInt(sequence[i]['expand']);
               console.log(sequence[i]['expand']);
               if (expand) {
                   expand_option_input.checked = true;
               }
               viewlink.setAttribute('href','/collection/'+sequence[i]["internal_title"])
               how_many.remove();
           } else {
               how_many.remove()
               expand_option.remove()
               viewlink.setAttribute('href','/comic/'+sequence[i]["internal_title"])
           }
           sequence_editor.append(clone)
       }
    };

        let very_simple_test = function () {
            console.log('ta-da!')
        }