import vue from "@vitejs/plugin-vue";

export default {
  plugins: [vue()],
  base: "./",
  build: {
    lib: {
      entry: "./src/main.js",
      name: "trame_simput",
      formats: ["umd"],
      fileName: "vue3-trame_simput",
    },
    minify: false,
    sourceMap: true,
    rollupOptions: {
      external: ["vue"],
      output: {
        globals: {
          vue: "Vue",
        },
      },
    },
    outDir: "../src/trame_simput/module/serve",
    assetsDir: ".",
  },
};
