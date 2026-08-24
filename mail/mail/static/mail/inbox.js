let currentMailbox = 'inbox';

document.addEventListener('DOMContentLoaded', function() {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);
  document.querySelector('#compose-form').addEventListener('submit', send_email);

  // By default, load the inbox
  load_mailbox('inbox');
});

function compose_email() {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#email-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';
}

function load_mailbox(mailbox) {

  currentMailbox = mailbox;

  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#email-view').style.display = 'none';

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

  fetch(`/emails/${mailbox}`)
    .then(response => response.json())
    .then(emails => {
      emails.forEach(email => {
        const element = document.createElement('div');
        element.classList.add('email-item');
        element.classList.add(email.read ? 'read' : 'unread');
        element.innerHTML = `
          <strong>From:</strong> ${email.sender}<br>
          <strong>Subject:</strong> ${email.subject}<br>
          <strong>Timestamp:</strong> ${email.timestamp}
        `;
        element.addEventListener('click', () => view_email(email.id));
        document.querySelector('#emails-view').append(element);
      });
    });
}

function send_email(event) {

  event.preventDefault();

  fetch('/emails', {
    method: 'POST',
    body: JSON.stringify({
      recipients: document.querySelector('#compose-recipients').value,
      subject: document.querySelector('#compose-subject').value,
      body: document.querySelector('#compose-body').value
    })
  })
    .then(response => response.json())
    .then(result => {
      load_mailbox('sent');
    });
}

function view_email(id) {

  fetch(`/emails/${id}`)
    .then(response => response.json())
    .then(email => {
      document.querySelector('#emails-view').style.display = 'none';
      document.querySelector('#compose-view').style.display = 'none';
      document.querySelector('#email-view').style.display = 'block';

      let buttons = '';
      if (currentMailbox === 'inbox') {
        buttons = `<button class="btn btn-sm btn-outline-primary" id="archive">Archive</button>`;
      } else if (currentMailbox === 'archive') {
        buttons = `<button class="btn btn-sm btn-outline-primary" id="unarchive">Unarchive</button>`;
      }

      document.querySelector('#email-view').innerHTML = `
        <p><strong>From:</strong> ${email.sender}</p>
        <p><strong>To:</strong> ${email.recipients.join(', ')}</p>
        <p><strong>Subject:</strong> ${email.subject}</p>
        <p><strong>Timestamp:</strong> ${email.timestamp}</p>
        <hr>
        <p>${email.body.replace(/\n/g, '<br>')}</p>
        <button class="btn btn-sm btn-outline-primary" id="reply">Reply</button>
        ${buttons}
      `;

      document.querySelector('#reply').addEventListener('click', () => reply(email));

      if (currentMailbox === 'inbox') {
        document.querySelector('#archive').addEventListener('click', () => {
          fetch(`/emails/${id}`, {
            method: 'PUT',
            body: JSON.stringify({ archived: true })
          })
            .then(() => load_mailbox('inbox'));
        });
      } else if (currentMailbox === 'archive') {
        document.querySelector('#unarchive').addEventListener('click', () => {
          fetch(`/emails/${id}`, {
            method: 'PUT',
            body: JSON.stringify({ archived: false })
          })
            .then(() => load_mailbox('inbox'));
        });
      }

      if (!email.read) {
        fetch(`/emails/${id}`, {
          method: 'PUT',
          body: JSON.stringify({ read: true })
        });
      }
    });
}

function reply(email) {

  compose_email();

  document.querySelector('#compose-recipients').value = email.sender;

  if (email.subject.startsWith('Re: ')) {
    document.querySelector('#compose-subject').value = email.subject;
  } else {
    document.querySelector('#compose-subject').value = `Re: ${email.subject}`;
  }

  document.querySelector('#compose-body').value =
    `On ${email.timestamp} ${email.sender} wrote:\n${email.body}`;
}
