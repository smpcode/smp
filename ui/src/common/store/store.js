class Store {
    constructor() {
        this.store = window.sessionStorage;
        this.prefix = "archapi_";
    }
    set(key, value, fn) {
        try {
            value = JSON.stringify(value);
        } catch (e) {
            value = value;
        }

        this.store.setItem(this.prefix + key, value);

        if (fn) {
            fn();
        }
    }
    get(key, fn) {
        if (!key) {
            throw new Error('没有找到key');
        }
        if (typeof key === 'object') {
            throw new Error('key不能是一个对象');
        }
        let value = this.store.getItem(this.prefix + key);
        if (value !== null) {
            try {
                value = JSON.parse(value);
            } catch (e) {
                value = value;
            }
        }

        return value;
    }
    remove(key) {
        this.store.removeItem(this.prefix + key);
    }
}
module.exports = new Store();
