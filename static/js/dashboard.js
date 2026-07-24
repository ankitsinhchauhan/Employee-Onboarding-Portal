(() => {
  "use strict";

  const storageKey = "dashboard_sidebar_collapsed";
  const body = document.body;
  const collapseButtons = document.querySelectorAll(
    '[data-dashboard-toggle="collapse-sidebar"]',
  );
  const sidebarButtons = document.querySelectorAll(
    '[data-dashboard-toggle="sidebar"]',
  );
  const sidebar = document.getElementById("dashboardSidebar");
  const header = document.querySelector(".dashboard-header");

  const isDesktop = () => window.matchMedia("(min-width: 992px)").matches;

  const setCollapsed = (collapsed) => {
    body.classList.toggle("sidebar-collapsed", collapsed);
    document.cookie = `${storageKey}=${collapsed ? "1" : "0"}; path=/; max-age=31536000; SameSite=Lax`;

    // Dispatch custom event for other scripts
    window.dispatchEvent(
      new CustomEvent("sidebarChange", {
        detail: { collapsed },
      }),
    );
  };

  // Restore sidebar state from cookie
  const initialCollapsed = document.cookie.includes(`${storageKey}=1`);
  if (initialCollapsed) {
    body.classList.add("sidebar-collapsed");
  }

  // Handle desktop sidebar collapse toggle
  collapseButtons.forEach((button) => {
    button.addEventListener("click", (e) => {
      e.stopPropagation();
      setCollapsed(!body.classList.contains("sidebar-collapsed"));
    });
  });

  // Handle sidebar toggle (mobile open / desktop collapse)
  sidebarButtons.forEach((button) => {
    button.addEventListener("click", (e) => {
      e.stopPropagation();

      if (isDesktop()) {
        // Desktop: collapse/expand sidebar
        setCollapsed(!body.classList.contains("sidebar-collapsed"));
        return;
      }

      // Mobile: toggle offcanvas sidebar
      if (!sidebar) return;

      const offcanvas = bootstrap.Offcanvas.getOrCreateInstance(sidebar);
      offcanvas.show();
    });
  });

  // Close sidebar on mobile when clicking outside
  document.addEventListener("click", (e) => {
    if (isDesktop()) return;
    if (!sidebar) return;

    const isSidebarClick = sidebar.contains(e.target);
    const isToggleClick = e.target.closest('[data-dashboard-toggle="sidebar"]');

    if (!isSidebarClick && !isToggleClick) {
      const offcanvas = bootstrap.Offcanvas.getInstance(sidebar);
      if (offcanvas && sidebar.classList.contains("show")) {
        offcanvas.hide();
      }
    }
  });

  // Handle window resize for responsive behavior
  let resizeTimer;
  window.addEventListener("resize", () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(() => {
      if (isDesktop()) {
        // On desktop, ensure sidebar state is consistent
        document.querySelectorAll(".dashboard-sidebar.show").forEach((el) => {
          const offcanvas = bootstrap.Offcanvas.getInstance(el);
          if (offcanvas) offcanvas.hide();
        });
      }
    }, 150);
  });

  // Animate progress bars on page load
  const animateProgressBars = () => {
    document.querySelectorAll(".progress-bar").forEach((bar) => {
      const width = bar.style.width || "0%";
      bar.style.width = "0%";
      setTimeout(() => {
        bar.style.width = width;
      }, 200);
    });
  };

  // Mark notification as read
  const markNotificationRead = (notificationId, button) => {
    if (!notificationId) return;

    fetch(`/employees/notifications/${notificationId}/read/`, {
      method: "POST",
      headers: {
        "X-CSRFToken": getCSRFToken(),
        "Content-Type": "application/json",
      },
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.status === "ok") {
          const row = button?.closest(".notification-row");
          if (row) {
            row.classList.remove("is-unread");
            const unreadBadge = row.querySelector(".status-badge.status-info");
            if (unreadBadge) unreadBadge.remove();
          }
          updateUnreadCount();
        }
      })
      .catch((err) => console.error("Error marking notification read:", err));
  };

  // Mark all notifications as read
  const markAllNotificationsRead = () => {
    fetch("/employees/notifications/mark-all-read/", {
      method: "POST",
      headers: {
        "X-CSRFToken": getCSRFToken(),
        "Content-Type": "application/json",
      },
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.status === "ok") {
          document.querySelectorAll(".notification-row").forEach((row) => {
            row.classList.remove("is-unread");
            const badge = row.querySelector(".status-badge.status-info");
            if (badge) badge.remove();
          });
          updateUnreadCount();
        }
      })
      .catch((err) =>
        console.error("Error marking all notifications read:", err),
      );
  };

  // Update unread notification count in the header
  const updateUnreadCount = () => {
    const dots = document.querySelectorAll(".notification-dot");
    const unreadPills = document.querySelectorAll(".unread-pill");

    dots.forEach((dot) => dot.remove());

    unreadPills.forEach((pill) => {
      const currentCount = parseInt(pill.textContent) || 0;
      pill.textContent = `${Math.max(0, currentCount - 1)} unread`;
    });
  };

  // Get CSRF token from cookie
  const getCSRFToken = () => {
    const name = "csrftoken";
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(";").shift();
    return "";
  };

  // Set up notification mark-as-read buttons
  document.querySelectorAll("[data-mark-read]").forEach((button) => {
    button.addEventListener("click", (e) => {
      const notificationId = button.getAttribute("data-mark-read");
      markNotificationRead(notificationId, button);
    });
  });

  // Set up mark-all-read buttons
  document.querySelectorAll("[data-mark-all-read]").forEach((button) => {
    button.addEventListener("click", (e) => {
      markAllNotificationsRead();
    });
  });

  // Animate progress bars after DOM is ready
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", animateProgressBars);
  } else {
    animateProgressBars();
  }

  // Expose utility functions globally
  window.OnboardHub = {
    markNotificationRead,
    markAllNotificationsRead,
    updateUnreadCount,
    setCollapsed,
  };
})();
