"use babel";
/* eslint-disable no-unused-vars */

// If you want to use ES6 module syntax, you will need "use babel" at the top of
// your resolver. Atom will transpile it automatically.
import path from "path";

// Custom resolver for js-hyperclick
// DOES NOT WORK
// https://github.com/AsaAyers/js-hyperclick/blob/master/custom-resolver.js
export default function customResolver({ basedir, moduleName }) {
  // You can use whatever strategy you want to convert your modules
  const [prefix, ...rest] = moduleName.split("/");

  // Whatever you return will be resolved realative to the file that imported
  // it.
  if (["~", "app", "sparrow"].includes(prefix)) {
    return path.resolve(path.join(__dirname, "..", "src", ...rest));
  }

  return moduleName;
}
