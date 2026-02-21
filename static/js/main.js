/* ============================================
   CMS — Main JavaScript
   ============================================ */

document.addEventListener('DOMContentLoaded', function () {

  /* ---------- Sidebar Toggle ---------- */
  const menuToggle = document.getElementById('menu-toggle');
  const sidebar = document.getElementById('sidebar');
  const overlay = document.getElementById('sidebar-overlay');

  if (menuToggle) {
    menuToggle.addEventListener('click', () => {
      sidebar.classList.toggle('open');
      if (overlay) overlay.classList.toggle('active');
    });
  }

  if (overlay) {
    overlay.addEventListener('click', () => {
      sidebar.classList.remove('open');
      overlay.classList.remove('active');
    });
  }

  /* ---------- Auto-dismiss flash messages ---------- */
  document.querySelectorAll('.alert').forEach(alert => {
    setTimeout(() => {
      alert.style.opacity = '0';
      alert.style.transform = 'translateX(-12px)';
      setTimeout(() => alert.remove(), 300);
    }, 5000);
  });

  document.querySelectorAll('.alert .close-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const alert = btn.closest('.alert');
      alert.style.opacity = '0';
      setTimeout(() => alert.remove(), 300);
    });
  });

  /* ---------- Dynamic Part Row (Assign Complaint) ---------- */
  const addPartBtn = document.getElementById('add-part-row');
  const partsBody = document.getElementById('parts-body');

  if (addPartBtn && partsBody) {
    addPartBtn.addEventListener('click', () => {
      const idx = partsBody.children.length;
      const partOptions = window.partOptionsHTML || '<option value="">Select Part</option>';
      const row = document.createElement('tr');
      row.innerHTML = `
        <td><select name="part" class="form-control">${partOptions}</select></td>
        <td><input type="number" name="quantity" class="form-control" value="1" min="1"></td>
        <td>
          <select name="source" class="form-control">
            <option value="new">New</option>
            <option value="used">Used</option>
            <option value="outsource">Outsource</option>
          </select>
        </td>
        <td><input type="text" name="notes" class="form-control" placeholder="Notes"></td>
        <td><button type="button" class="btn btn-danger btn-sm remove-part-row">✕</button></td>
      `;
      partsBody.appendChild(row);
    });

    partsBody.addEventListener('click', (e) => {
      if (e.target.classList.contains('remove-part-row')) {
        e.target.closest('tr').remove();
      }
    });
  }

  /* ---------- Resolve Complaint — Cost Calculator ---------- */
  const resolveForm = document.getElementById('resolve-form');
  if (resolveForm) {
    const serviceChargeInput = document.getElementById('service-charge');
    const grandTotalDisplay = document.getElementById('grand-total-display');
    const specialCheckboxes = document.querySelectorAll('.special-case-checkbox');

    function calcGrandTotal() {
      let partsTotal = 0;
      document.querySelectorAll('.part-row').forEach(row => {
        const qty = parseFloat(row.querySelector('.used-qty')?.value) || 0;
        const price = parseFloat(row.querySelector('.part-price')?.value) || 0;
        const lineTotal = qty * price;
        const lineTotalEl = row.querySelector('.line-total');
        if (lineTotalEl) lineTotalEl.textContent = lineTotal.toFixed(2);
        partsTotal += lineTotal;
      });

      const partsTotalEl = document.getElementById('parts-total');
      if (partsTotalEl) partsTotalEl.textContent = partsTotal.toFixed(2);

      const isSpecial = Array.from(specialCheckboxes).some(cb => cb.checked);
      const serviceCharge = isSpecial ? 0 : (parseFloat(serviceChargeInput?.value) || 0);

      if (serviceChargeInput && isSpecial) serviceChargeInput.value = 0;
      if (grandTotalDisplay) grandTotalDisplay.textContent = (isSpecial ? 0 : (serviceCharge + partsTotal)).toFixed(2);
    }

    resolveForm.addEventListener('input', calcGrandTotal);
    resolveForm.addEventListener('change', calcGrandTotal);

    // Exclusive checkboxes
    specialCheckboxes.forEach(cb => {
      cb.addEventListener('change', function() {
        if (this.checked) {
          specialCheckboxes.forEach(other => {
            if (other !== this) other.checked = false;
          });
        }
        calcGrandTotal();
      });
    });

    calcGrandTotal();
  }

  /* ---------- Active Nav Link ---------- */
  const currentPath = window.location.pathname;
  document.querySelectorAll('.nav-link').forEach(link => {
    const href = link.getAttribute('href');
    if (href && currentPath.startsWith(href) && href !== '/') {
      link.classList.add('active');
    }
  });

});
