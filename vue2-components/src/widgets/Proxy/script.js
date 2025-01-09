import SimputInput from '../../components/SimputItem';
import { COMPUTED, getComponentProps } from '../../core/utils';

export default {
  name: 'swProxy',
  props: {
    name: {
      type: String,
    },
    size: {
      type: Number,
      default: 1,
    },
    sizeControl: {
      type: Boolean,
      default: false,
    },
    proxyType: {
      type: String,
    },
    mtime: {
      type: Number,
    },
  },
  components: {
    SimputInput,
  },
  data() {
    return {
      dynamicSize: this.size,
    };
  },
  computed: {
    ...COMPUTED.decorator,
    model: {
      get() {
        /* eslint-disable no-unused-expressions */
        this.mtime; // force refresh
        this.dynamicSize;
        const value = this.properties() && this.properties()[this.name];
        if (!value && this.size > 1) {
          const emptyArray = [];
          emptyArray.length = this.size;
          return emptyArray;
        }
        return value;
      },
      set(v) {
        this.properties()[this.name] = v;
      },
    },
    itemId() {
      /* eslint-disable no-unused-expressions */
      this.mtime; // force refresh
      return this.properties()[this.name];
    },
    computedLayout() {
      /* eslint-disable no-unused-expressions */
      this.mtime; // force refresh
      return this.layout || this.domains()[this.name]?.UI?.layout || 'vertical';
    },
    computedSize() {
      if (Number(this.size) !== 1) {
        return Math.max(this.size || 1, this.model?.length || 0);
      }
      return Number(this.size);
    },
    computedSizeControl() {
      /* eslint-disable no-unused-expressions */
      this.mtime; // force refresh
      return this.sizeControl || this.domains()[this.name]?.UI?.sizeControl;
    },
  },
  methods: {
    getComponentProps(index) {
      return getComponentProps(this.computedLayout, index);
    },
    deleteEntry(index) {
      if (this.computedSize > Number(this.size)) {
        this.model.splice(index, 1);
        this.dirty(this.name);
      }
    },
  },
  inject: ['data', 'properties', 'domains', 'dirty'],
};
