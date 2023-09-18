import { UserConfig } from "vite";
import path from "path";
import { symlinkSync } from "fs";
import mdx from "@mdx-js/rollup";

function relativePath(...tokens) {
  return path.resolve(__dirname, ...tokens);
}

// Link site content into frontend cache directory
const siteContent =
  process.env.SPARROW_SITE_CONTENT || relativePath("default-content");
let contentDir = relativePath(".yarn/cache/site-content");
try {
  symlinkSync(siteContent, contentDir, "dir");
} catch {
  console.log("Symlink already exists");
}

const config: UserConfig = {
  cacheDir: path.resolve(".vite"),
  root: "./src",
  plugins: [
    mdx({
      mdxExtensions: [".mdx", ".md"],
      mdExtensions: [],
    }),
  ],
  resolve: {
    conditions: ["typescript"],
    alias: {
      "~": path.resolve("./src"),
      app: path.resolve("./src"),
      sparrow: path.resolve("./src"),
      "site-content": contentDir,
    },
    preserveSymlinks: true,
  },
  define: {
    global: {},
  },
};

export default config;
