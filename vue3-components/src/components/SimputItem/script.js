import VRuntimeTemplate from "vue3-runtime-template";
const { ref, computed, onMounted, onBeforeUnmount, watch, provide, inject } =
  window.Vue;

export default {
  name: "SimputItem",
  emits: ["dirty"],
  props: {
    itemId: {
      type: String,
    },
    noUi: {
      type: Boolean,
      default: false,
    },
  },
  components: {
    VRuntimeTemplate,
  },
  data() {
    return {
      data: null,
    };
  },
  setup(props) {
    const simputChannel = inject("simputChannel");
    const getSimput = inject("getSimput");

    const data = ref(null);
    const ui = ref(null);
    const domains = ref(null);

    const computedType = computed(() => data.value && data.value.type);

    const proxyId = computed(() => `${props.itemId}`);

    const update = function update() {
      if (proxyId.value && getSimput()) {
        console.log("SimputItem - update");
        console.log({
          proxyId: proxyId.value,
        });
        data.value = getSimput().getData(proxyId.value);
        domains.value = getSimput().getDomains(proxyId.value);

        console.log({
          data: data.value,
          domains: domains.value,
          computedType: computedType.value,
        });

        if (computedType.value) {
          ui.value = getSimput().getUI(computedType.value);
          console.log({
            ui: ui.value,
          });
        }
        simputChannel.pushQuery();
      } else {
        console.log("SimputItem - update: reset data and ui")
        data.value = null;
        ui.value = null;
      }
    };

    const onConnect = function onConnect() {
      update();
    };

    const onChange = function onChange({ id, type }) {
      /* eslint-disable eqeqeq */
      if (id && proxyId.value == id) {
        console.log("SimputItem - onChange");
        data.value = getSimput().getData(id);
        domains.value = getSimput().getDomains(id);
        console.log({
          data: data.value,
          domains: domains.value,
        });
      }
      if (type && computedType.value === type) {
        ui.value = getSimput().getUI(computedType.value);
      }
      if (!type && computedType.value && !ui.value) {
        ui.value = getSimput().getUI(computedType.value);
      }
      console.log({
        ui: ui.value,
      });
    };

    const onReload = function onReload(name) {
      console.log("SimputItem - onReload");
      if (name === "data") {
        data.value = getSimput().getData(proxyId.value, true);
        console.log({
          data: data.value,
        });
      }
      if (name === "ui") {
        ui.value = getSimput().getUI(proxyId.value, true);
        console.log({
          ui: ui.value,
        });
      }
      if (name === "domain") {
        getSimput().resetDomains();
        domains.value = getSimput().getDomains(proxyId.value, true);
        console.log({
          domains: domains.value,
        });
      }
    };

    onMounted(() => {
      simputChannel.$on("connect", onConnect);
      simputChannel.$on("change", onChange);
      simputChannel.$on("reload", onReload);
      console.log("SimputItem - onMounted");
      update();
    });

    onBeforeUnmount(() => {
      simputChannel.$off("connect", onConnect);
      simputChannel.$off("change", onChange);
      simputChannel.$off("reload", onReload);
    });

    const available = computed(
      () => !!(data.value && domains.value && ui.value)
    );
    const properties = computed(() => data.value?.properties);

    const all = computed(() => {
      return {
        id: proxyId.value,
        data: data.value,
        domains: domains.value,
        properties: properties.value,
      };
    });

    const dirty = function dirty(name) {
      simputChannel.$emit("dirty", { id: data.value?.id, name });
    };

    const dirtyMany = function dirtyMany(names) {
      simputChannel.$emit("dirty", { id: data.value?.id, names });
    };

    watch(
      () => props.itemId,
      () => {
        // Clear previous data if its a different proxy
        data.value = null;
        ui.value = null;

        // Update data to match given itemId
        update();
      }
    );

    provide("dirty", (name) => dirty(name));
    provide("dirtyMany", (...names) => dirtyMany(names));
    provide("data", () => data.value);
    provide("domains", () => domains.value);
    provide("properties", () => properties.value);
    provide("uiTS", () => getSimput().getUITimeStamp());

    return {
      available,
      all,
      properties,
      ui,
      data,
    };
  },
};
