import { TYPES, FALLBACK_CONVERT } from './types';

export const MANAGERS = {};

export const COMPUTED = {
  query: {
    textToQuery() {
      // ${this.help?.toLowerCase() || ''}
      return `${this.name?.toLowerCase() || ''} ${this.label?.toLowerCase() ||
        ''}`;
    },
    shouldShow() {
      if (this.query && this.decorator.query) {
        const tokens = this.query.split(' ');
        if (tokens.length > 1) {
          for (let i = 0; i < tokens.length; i++) {
            const t = tokens[i].trim();
            if (t && this.textToQuery.includes(t)) {
              return true;
            }
          }
          return false;
        }
        return this.textToQuery.includes(this.query);
      }
      return this.decorator.show;
    },
  },
  decorator: {
    decorator() {
      /* eslint-disable no-unused-expressions */
      this.mtime; // force refresh
      return (
        this.domains()[this.name]?.decorator?.available || {
          show: true,
          enable: true,
          query: true,
        }
      );
    },
  },
  convert: {
    convert() {
      return TYPES[this.type]?.convert || FALLBACK_CONVERT;
    },
  },
  hints: {
    hints() {
      /* eslint-disable no-unused-expressions */
      this.mtime; // force refresh
      return this.domains()?.[this.name]?.hints || [];
    },
  },
  rule: {
    rule() {
      return TYPES[this.type]?.rule || (() => true);
    },
  },
};

export function debounce(func, wait = 100) {
  let timeout;
  const debounced = (...args) => {
    const context = this;
    const later = () => {
      timeout = null;
      func.apply(context, args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };

  debounced.cancel = () => clearTimeout(timeout);

  return debounced;
}

export class DataManager {
  constructor(namespace, wsClient) {
    this.namespace = namespace;
    this.cache = null;
    this.comm = [];
    this.pendingData = {};
    this.pendingDomain = {};
    this.pendingUI = {};
    this.pendingDirtyData = {};
    this.wsClient = wsClient;
    this.resetCache();
    this.nextTS = 1;
    this.dirtySet = [];
    this.expectedServerProps = {};
    this.subscription = this.wsClient
      .getConnection()
      .getSession()
      .subscribe('simput.push', ([event]) => {
        const { id, data, domains, type, ui } = event;
        let idChange = false;
        let uiChange = false;
        if (data) {
          delete this.pendingData[id];
          delete this.pendingDirtyData[id];
          const before = JSON.stringify(this.expectedServerProps[id]);
          const after = JSON.stringify(data.properties);
          if (before !== after) {
            idChange = true;
            this.cache.data[id] = data;
            if (before == undefined) {
              this.expectedServerProps[id] = JSON.parse(
                JSON.stringify(data.properties)
              ); // deep copy
            }
            //   console.log(`data(${id}) == CHANGE`);
            //   // console.group('before');
            //   // console.log(before);
            //   // console.groupEnd();
            //   // console.group('after');
            //   // console.log(after);
            //   // console.groupEnd();
            // } else {
            //   console.log(`data(${id}) == SAME`);
          }
          this.cache.data[id].mtime = data.mtime;
          this.cache.data[id].original = JSON.parse(after);
        }
        if (domains) {
          delete this.pendingDomain[id];
          const before = JSON.stringify(this.cache.domains[id]);
          const after = JSON.stringify(domains);
          // console.log(JSON.stringify(domains, null, 2));
          if (before !== after) {
            idChange = true;
            this.cache.domains[id] = domains;
            // console.log(`domains(${id}) == CHANGE`);
            // } else {
            //   console.log(`domains(${id}) == SAME`);
          }
        }
        if (ui) {
          uiChange = true;
          // console.log(`ui(${type})`);
          delete this.pendingUI[type];
          this.cache.ui[type] = ui;
        }

        const notifyPayload = {};
        if (idChange) {
          notifyPayload.id = id;
        }
        if (uiChange) {
          notifyPayload.type = type;
        }

        this.notify('change', notifyPayload);
        if (ui) {
          this.nextTS += 1;
          this.notify('templateTS');
        }

        this.flushDirtySet();
      });
    this.subscriptionUI = this.wsClient
      .getConnection()
      .getSession()
      .subscribe('simput.event', ([event]) => {
        if (event.topic === 'ui-change') {
          const typesToFetch = Object.keys(this.cache.ui);
          this.cache.ui = {};
          for (let i = 0; i < typesToFetch.length; i++) {
            this.getUI(typesToFetch[i]);
          }
        }
        if (event.topic === 'data-change') {
          const { ids, action } = event;
          for (let i = 0; i < ids.length; i++) {
            if (this.cache.data[ids[i]]) {
              if (action === 'changed') {
                // console.log('getData from data-change', ids[i]);
                this.getData(ids[i], true);
              }
            }
          }
        }
      });

    this.onDirty = ({ id, name, names }) => {
      if (name) {
        const value = this.cache.data[id].properties[name];
        let idx = this.dirtySet.findIndex(
          (e) => e.id === id && e.name === name
        );
        if (idx > -1) this.dirtySet.splice(idx, 1);
        this.dirtySet.push({ id, name, value });
      }
      if (names) {
        for (let i = 0; i < names.length; i++) {
          const name = names[i];
          const value = this.cache.data[id].properties[name];
          let idx = this.dirtySet.findIndex(
            (e) => e.id === id && e.name === name
          );
          if (idx > -1) this.dirtySet.splice(idx, 1);
          this.dirtySet.push({ id, name, value });
        }
      }

      // console.log(' > dirty', [...this.dirtySet]);
      this.flushDirtySet();
    };
  }

  async flushDirtySet() {
    if (!this.dirtySet.length) {
      return;
    }

    if (Object.keys(this.pendingDirtyData).length) {
      return;
    }

    const dirtySet = this.dirtySet;
    this.dirtySet = [];
    dirtySet.forEach(({ id, name, value }) => {
      this.expectedServerProps[id][name] = value;
      this.pendingDirtyData[id] = true;
    });
    // console.log('sending: ', dirtySet);
    await this.wsClient
      .getRemote()
      .Trame.trigger(`${this.namespace}Update`, [dirtySet]);

    this.flushDirtySet();
  }

  resetCache() {
    this.cache = {
      data: {},
      ui: {},
      domains: {},
    };
    this.wsClient.getRemote().Trame.trigger(`${this.namespace}ResetCache`, []);
  }

  resetDomains() {
    this.cache.domains = {};
  }

  connectBus(bus) {
    if (this.comm.indexOf(bus) === -1) {
      this.comm.push(bus);
      bus.$emit('connect');
      bus.$on('dirty', this.onDirty);
    }
  }

  disconnectBus(bus) {
    const index = this.comm.indexOf(bus);
    if (index > -1) {
      bus.$emit('disconnect');
      bus.$off('dirty', this.onDirty);
      this.comm.splice(index, 1);
    }
  }

  notify(topic, event) {
    for (let i = 0; i < this.comm.length; i++) {
      this.comm[i].$emit(topic, event);
    }
  }

  getData(id, forceFetch = false) {
    const data = this.cache.data[id];
    if ((!data || forceFetch) && !this.pendingData[id]) {
      // console.log(' > fetch data', id, forceFetch);
      this.pendingData[id] = true;
      this.wsClient
        .getRemote()
        .Trame.trigger(`${this.namespace}Fetch`, [], { id });
    }

    return data;
  }

  getDomains(id, forceFetch = false) {
    const domains = this.cache.domains[id];

    if ((!domains || forceFetch) && !this.pendingDomain[id]) {
      // console.log(' > fetch domain', id, forceFetch);
      this.pendingDomain[id] = true;
      this.wsClient
        .getRemote()
        .Trame.trigger(`${this.namespace}Fetch`, [], { domains: id });
    }

    return domains;
  }

  getUI(type, forceFetch = false) {
    const ui = this.cache.ui[type];

    if ((!ui || forceFetch) && !this.pendingUI[type]) {
      // console.log(' > fetch ui', type, forceFetch);
      this.pendingUI[type] = true;
      this.wsClient
        .getRemote()
        .Trame.trigger(`${this.namespace}Fetch`, [], { type });
    }

    return ui;
  }

  getUITimeStamp() {
    return this.nextTS;
  }

  refresh(id, name) {
    // console.log(' > refresh', id, name);
    this.wsClient
      .getRemote()
      .Trame.trigger(`${this.namespace}Refresh`, [id, name]);
  }
}

export function getSimputManager(id, namespace, client) {
  if (!client) {
    return null;
  }

  if (MANAGERS[id]) {
    return MANAGERS[id];
  }

  const manager = new DataManager(namespace, client);
  MANAGERS[id] = manager;
  return manager;
}
