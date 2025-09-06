const alreadyCollapsed = new WeakSet();

function autoCollapseSteps(element) {
  if (element.matches?.('button[id^="step-"]')) {
    tryCollapse(element);
  }
  element.querySelectorAll?.('button[id^="step-"]').forEach((btn) => {
    tryCollapse(btn);
  });
}

function tryCollapse(btn) {
  const isOpen = btn.getAttribute('data-state') === 'open';
  if (
    isOpen &&
    !alreadyCollapsed.has(btn) &&
    btn.querySelector('svg.lucide-chevron-up') // icon for expanded state
  ) {
    btn.click(); // close it
    alreadyCollapsed.add(btn);
  }
}

function removeCopyButtons() {
  document.querySelectorAll('button').forEach((button) => {
    if (button.querySelector('.lucide-copy')) {
      button.remove();
    }
  });
}

removeCopyButtons();

const mutationObserver = new MutationObserver((mutationList) => {
  for (const mutation of mutationList) {
    if (mutation.type === 'childList') {
      for (const node of mutation.addedNodes) {
        if (node.nodeType === Node.ELEMENT_NODE) {
          autoCollapseSteps(node);
        }
      }
    }
  }
});

mutationObserver.observe(document.body, {
  childList: true,
  subtree: true,
});

const copyButtonObserver = new MutationObserver(() => {
  removeCopyButtons();
});

copyButtonObserver.observe(document.body, {
  childList: true,
  subtree: true,
});

document.querySelectorAll('button[id^="step-"]').forEach(autoCollapseSteps);

