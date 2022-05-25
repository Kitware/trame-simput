import SimputInput from '../../components/SimputItem';
import { COMPUTED } from '../../core/utils';

export default {
  name: 'swProxy',
  props: {
    name: {
      type: String,
    },
    mtime: {
      type: Number,
    },
  },
  components: {
    SimputInput,
  },
  computed: {
    ...COMPUTED.decorator,
    itemId() {
      /* eslint-disable no-unused-expressions */
      this.mtime; // force refresh
      return this.properties()[this.name];
    },
  },
  inject: ['data', 'properties', 'domains', 'dirty'],
};
