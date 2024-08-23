{
    const oauth0Redirect = window.sessionStorage.getItem('oauth0-redirect');
    const currentPath = window.location.origin + window.location.pathname;
    if ((null != oauth0Redirect) && (currentPath != oauth0Redirect)) {
        window.open(oauth0Redirect + window.location.search, "_self");
    }
}
