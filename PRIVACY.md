# Privacy and data handling / Tietosuoja ja tietojen käsittely

**Repository / Projekti:** Remote Job Fit  
**Last reviewed / Tarkistettu:** 11 November 2026

## Suomeksi

### Soveltamisala
Remote Job Fit on ensisijaisesti käyttäjän omalla tietokoneella suoritettava kokeellinen työkalu. Sovellus käsittelee käyttäjän paikallista profiilitiedostoa, SQLite-tietokantaa, työpaikkailmoituksia ja mahdollisia CSV-vientejä paikallisesti. Se hakee ilmoituksia käyttäjän käynnistämänä tuetuista ulkoisista lähteistä (Remotive ja Remote OK); nämä palvelut saavat tavanomaisia verkkopyyntöihin liittyviä teknisiä tietoja. Valinnainen sähköpostikooste lähettää viestin vain, jos käyttäjä määrittää omat SMTP-asetuksensa ja käynnistää toiminnon. Projekti ei siirrä paikallista profiilia projektin ylläpitäjälle eikä sisällä omaa analytiikkaa tai evästeitä. GitHub Pages -selaindemo on erillinen yksinkertaistettu esimerkki, eikä se käytä paikallista Python-backendia tai hae live-ilmoituksia.

### Rekisterinpitäjä ja yhteydenotot
Tämän projektin lähdekoodin ja dokumentaation ylläpitäjä on Marika Matalamäki. Tietosuojaa koskevat kysymykset voi lähettää osoitteeseen marika.matalamaki@gmail.com. Tämä yhteystieto ei tarkoita, että projekti keräisi kävijöiden henkilötietoja.

### Evästeet ja analytiikka
Projektin ylläpitäjä ei lisää tähän projektiin omia mainos- tai seurantaevästeitä eikä omaa analytiikkapalvelua, ellei tässä dokumentissa tai sovelluksen dokumentaatiossa nimenomaisesti toisin kerrota. GitHubin, GitHub Pagesin, hosting-palvelun ja ulkoisten palveluiden tekninen tietojenkäsittely määräytyy niiden omien tietosuojakäytäntöjen mukaan. Jos projektin toiminnallisuus tai palveluntarjoajat muuttuvat, tämä dokumentti päivitetään.

### Oikeudet ja lisätiedot
Voit pyytää itseäsi koskevien mahdollisten projektin ylläpitäjän hallussa olevien tietojen tarkastamista tai poistamista ottamalla yhteyttä yllä mainittuun sähköpostiosoitteeseen. Lakisääteiset oikeudet riippuvat siitä, käsitelläänkö henkilötietoja ja millä oikeusperusteella. GitHubin omiin tietoihin liittyvät pyynnöt tulee osoittaa GitHubille.

## English

### Scope
Remote Job Fit is an experimental tool intended to run primarily on the user's own computer. It processes the user's local profile file, SQLite database, job listings and optional CSV exports locally. When the user runs a search, it requests listings from supported external sources (Remotive and Remote OK); those providers receive ordinary technical information associated with web requests. The optional email digest sends messages only when the user configures their own SMTP settings and runs the feature. The project does not send local profile data to its maintainer and does not include its own analytics or cookies. The GitHub Pages browser demo is a separate simplified example; it does not run the local Python backend or fetch live listings.

### Controller and contact
The source code and documentation for this project are maintained by Marika Matalamäki. Privacy questions can be sent to marika.matalamaki@gmail.com. This contact detail does not mean that the project collects visitor personal data.

### Cookies and analytics
The project maintainer does not add project-owned advertising or tracking cookies or a project-owned analytics service unless expressly stated in this document or the application documentation. Technical processing by GitHub, GitHub Pages, a hosting provider and external services is governed by their own privacy notices. This document should be updated if the project's functionality or providers change.

### Rights and further information
You may contact the maintainer at the email address above to ask about access to or deletion of any personal data about you that the maintainer may hold in connection with the project. The availability of statutory rights depends on whether personal data is processed and on the applicable legal basis. Requests concerning data held by GitHub should be directed to GitHub.

## Related documents
- [Security policy](SECURITY.md)
- [Copyright and permitted use](COPYRIGHT.md)
- [GitHub Privacy Statement](https://docs.github.com/en/site-policy/privacy-policies/github-privacy-statement)
