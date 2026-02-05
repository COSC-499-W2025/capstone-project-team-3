/**
 * Automatically exports all pages
 * Just add a new .tsx file in pages/
 */

const pages = import.meta.glob<{ default: React.FC }>('./*.tsx', { eager: true });

interface Page {
  path: string;
  component: React.FC;
}

export const pageList: Page[] = Object.entries(pages).map(([filePath, module]) => {
  const name = filePath
    .replace('./', '')
    .replace('.tsx', '')
    .toLowerCase(); // route path

  return {
    path: `/${name}`,
    component: module.default,
  };
});
