import { getSimputManager, debounce } from '../../core/utils';

export default {
  name: 'Simput',
  props: {
    wsClient: {
      type: Object,
    },
    namespace: {
      type: String,
      default: 'simput',
    },
    query: {
      type: String,
      default: '',
    },
  },
  created() {
    this.updateManager();
    this.pushQuery = debounce(
      () => this.$emit('query', this.query?.toLowerCase() || ''),
      250
    );
  },
  beforeDestroy() {
    if (this.manager) {
      this.manager.disconnectBus(this);
    }
    this.manager = null;
  },
  watch: {
    namespace() {
      this.updateManager();
    },
    query() {
      this.pushQuery();
    },
  },
  computed: {
    client() {
      return this.wsClient || this.trame.client;
    },
  },
  methods: {
    updateManager() {
      if (!this.client) {
        return;
      }

      if (this.manager) {
        this.manager.disconnectBus(this);
      }

      this.managerId = this.trame.state.get(`${this.namespace}Id`);
      this.manager = getSimputManager(
        this.managerId,
        this.namespace,
        this.client
      );
      this.manager.connectBus(this);
    },
    reload(name) {
      this.manager.notify('reload', name);
    },
  },
  provide() {
    return {
      simputChannel: this,
      getSimput: () => this.manager,
    };
  },
  inject: ['trame'],
};
