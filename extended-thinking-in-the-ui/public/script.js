const alreadyExpanded = new WeakSet();

function autoOpenSteps(element) {
  if (element.matches?.('button[id^="step-"]')) {
    tryExpand(element);
  }
  element.querySelectorAll?.('button[id^="step-"]').forEach((btn) => {
    tryExpand(btn);
  });
}

function tryExpand(btn) {
  const isClosed = btn.getAttribute('data-state') === 'closed';
  if (
    isClosed &&
    !alreadyExpanded.has(btn) &&
    btn.querySelector('svg.lucide-chevron-down')
  ) {
    btn.click();
    alreadyExpanded.add(btn);
  }
}

function removeCopyButtons() {
  document.querySelectorAll('button[data-state="closed"]').forEach((button) => {
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
          autoOpenSteps(node);
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

document.querySelectorAll('button[id^="step-"]').forEach(autoOpenSteps);
