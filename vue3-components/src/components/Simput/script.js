const { ref, computed, onMounted, onBeforeUnmount, watch, provide, inject } =
  window.Vue;
import { getSimputManager, debounce } from "../../core/utils";
import mitt from "mitt";

const emitter = mitt();

export default {
  name: "Simput",
  emits: ["query"],
  props: {
    wsClient: {
      type: Object,
    },
    namespace: {
      type: String,
      default: "simput",
    },
    query: {
      type: String,
      default: "",
    },
  },
  setup(props, { emit }) {
    const trame = inject("trame");

    const manager = ref(null);
    const managerId = ref(null);

    const client = computed(() => props.wsClient || trame.client);

    const simputChannel = {
      $on: (...args) => emitter.on(...args),
      $once: (...args) => emitter.once(...args),
      $off: (...args) => emitter.off(...args),
      $emit: (...args) => emitter.emit(...args),
      pushQuery: debounce(
        () => emit("query", props.query?.toLowerCase() || ""),
        250
      ),
      managerId,
    };

    const updateManager = function updateManager() {
      if (!client.value) {
        return;
      }

      if (manager.value) {
        manager.value.disconnectBus(simputChannel);
      }

      managerId.value = trame.state.get(`${props.namespace}Id`);

      manager.value = getSimputManager(
        managerId.value,
        props.namespace,
        client.value
      );

      manager.value.connectBus(simputChannel);
    };

    onMounted(() => {
      updateManager();
    });

    onBeforeUnmount(() => {
      if (manager.value) {
        manager.value.disconnectBus(simputChannel);
      }
      manager.value = null;
    });

    watch(() => props.namespace, updateManager);
    watch(() => props.query, simputChannel.pushQuery);

    const reload = function reload(name) {
      manager.value.notify("reload", name);
    };

    provide("simputChannel", simputChannel);
    provide("getSimput", () => manager.value);

    return {
      updateManager,
      reload,
    };
  },
};
