class CreateApiKeys < ActiveRecord::Migration[7.0]
  def change
    create_table :api_keys do |t|
      t.string :key, null: false
      t.string :name, null: false
      t.boolean :active, default: true
      t.timestamps
    end
    
    add_index :api_keys, :key, unique: true
    add_index :api_keys, :active
  end
end 