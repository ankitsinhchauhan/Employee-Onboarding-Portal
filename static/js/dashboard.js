(() => {
  const storageKey = "dashboard_sidebar_collapsed";
  const body = document.body;
  const collapseButtons = document.querySelectorAll(
    '[data-dashboard-toggle="collapse-sidebar"]',
  );
  const sidebarButtons = document.querySelectorAll(
    '[data-dashboard-toggle="sidebar"]',
  );
  const sidebar = document.getElementById("dashboardSidebar");

  const isDesktop = () => window.matchMedia("(min-width: 992px)").matches;

  const setCollapsed = (collapsed) => {
    body.classList.toggle("sidebar-collapsed", collapsed);
    document.cookie = `${storageKey}=${collapsed ? "1" : "0"}; path=/; max-age=31536000; SameSite=Lax`;
  };

  const initialCollapsed = document.cookie.includes(`${storageKey}=1`);
  if (initialCollapsed) {
    body.classList.add("sidebar-collapsed");
  }

  // collapseButtons.forEach((button) => {
  //   button.addEventListener("click", () => {
  //     setCollapsed(!body.classList.contains("sidebar-collapsed"));
  //   });
  // });

  sidebarButtons.forEach((button) => {
    button.addEventListener("click", () => {
      if (isDesktop()) {
        setCollapsed(!body.classList.contains("sidebar-collapsed"));
        return;
      }

      if (!sidebar) {
        return;
      }

      const offcanvas = bootstrap.Offcanvas.getOrCreateInstance(sidebar);
      offcanvas.show();
    });
  });
})();
