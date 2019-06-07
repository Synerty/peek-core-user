.. _core_device_admin_ui_settings:

Admin UI Settings
-----------------

Home
````

Configure the General Settings to configure the user plugin.

.. image:: home.png

Logged In Users
```````````````

This screen shows the logged in users in Peek. Administrators can logout users from
from this screen.

.. image:: manage-logged-in-users.png

Edit Internal Users
```````````````````

This screen is used to configure the internal users in Peek.

When LDAP is enabled, users will appear in this screen when they first login.

.. note:: Internal users can be imported from other systems.

.. image:: edit-internal-user.png

Edit Internal Groups
````````````````````

This screen is used to configure the internal groups in Peek.

Internal groups are not used when the authentication is set to LDAP.

.. note:: Internal groups can be imported from other systems.


.. image:: edit-internal-groups.png

Edit General Settings
`````````````````````

Configure the General Settings to configure the user plugin.

:Mobile Login Group: Users in this group will show when the login screen shows a user
    list instead of a text box.

:Show Vehicle Input: Should the Peek login screen show a box to take the users
    vehicle ID.

:Show Login as List: Should the Peek login screen show a list of users, or an
    input box for a user name. (See Mobile Login Group)

.. image:: settings-general.png

Edit LDAP Settings
``````````````````

Configure the LDAP Settings to configure the user plugin.

Attunes LDAP works seamlessly against the Microsoft Active Directory
Lightweight Directory Service (AD LDS).

----

The following is a good article that describes how to enable LDAP over SSL (LDAPS)
on Windows 2012.

`<https://social.technet.microsoft.com/wiki/contents/articles/2980.ldap-over-ssl-ldaps-certificate.aspx>`_

----

To configure LDAP:

#.  Select the **LDAP Settings** from the settings dropdown box,

#.  Set the LDAP settings, including "LDAP Enabled"

#.  Click Save

Now attempt to login with an LDAP user.

----

.. image:: settings-ldap.png

----

:LDAP Enabled: Should Peek attempt LDAP authentication at all.
    If LDAP authentication is disabled, Peek will authenticate against the internal
    password table.

:LDAP Domain Name: The domain name of the LDAP installation,
    for example :code:`domain.example.org` where domain.example.org is the name of your
    active directory domain.

:LDAP URI: The connection string to the LDAP server, example values are:

    *  :code:`ldap://server1.example.org`

    *  :code:`ldap://domain.example.org`

    *  :code:`ldaps://10.2.2.2`

:LDAP CN Folders: This is a comma separated lost of CN paths to search during login

:LDAP OU Folders: TThis is a comma separated lost of OU paths to search during login


